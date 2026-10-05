from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from config import Config
from extensions import db
from models.order import CartItem, Order
from models.payment import Payment
from routes.orders import create_order_from_cart
from services.mpesa import MpesaError, MpesaService

payments_bp = Blueprint("payments", __name__, url_prefix="/api/payments")


def _sync_order_payment_fields(order: Order, payment: Payment) -> None:
    order.status = payment.status
    order.phone = payment.phone
    order.checkout_request_id = payment.checkout_request_id
    order.mpesa_receipt = payment.mpesa_receipt


def _create_payment(order: Order, phone: str, status: str = "pending") -> Payment:
    payment = Payment(
        order_id=order.id,
        amount=order.total,
        provider="mpesa",
        status=status,
        phone=phone,
    )
    db.session.add(payment)
    db.session.flush()
    _sync_order_payment_fields(order, payment)
    return payment


def _finalize_paid_order(order: Order, user_id: int) -> None:
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        db.session.commit()
        return
    for item in order.items:
        if item.product:
            item.product.stock -= item.quantity
    for cart_item in cart_items:
        db.session.delete(cart_item)
    db.session.commit()


@payments_bp.get("/mpesa/config")
def mpesa_public_config():
    """Public sandbox/live flags for the checkout UI (no secrets)."""
    missing = MpesaService.missing_config_keys()
    has_partial = bool(Config.MPESA_CONSUMER_KEY or Config.MPESA_CONSUMER_SECRET)
    return jsonify(
        {
            "env": Config.MPESA_ENV,
            "configured": MpesaService.is_configured(),
            "missing": missing,
            "partial_credentials": has_partial and not MpesaService.is_configured(),
            "shortcode": Config.MPESA_SHORTCODE if Config.MPESA_SHORTCODE else None,
            "sandbox_test_msisdn": "254708374149" if Config.MPESA_ENV == "sandbox" else None,
        }
    )


@payments_bp.post("/mpesa/stk-push")
@jwt_required()
def mpesa_stk_push():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    phone = (data.get("phone") or "").strip()

    if not phone:
        return jsonify({"error": "Phone number is required"}), 400

    cart_count = CartItem.query.filter_by(user_id=user_id).count()
    if cart_count == 0:
        return jsonify({"error": "Cart is empty"}), 400

    try:
        normalized_phone = MpesaService.normalize_phone(phone)
        order = create_order_from_cart(user_id, phone=normalized_phone)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    payment = _create_payment(order, normalized_phone, status="pending")

    if not MpesaService.is_configured():
        missing = MpesaService.missing_config_keys()
        if Config.MPESA_CONSUMER_KEY or Config.MPESA_CONSUMER_SECRET:
            payment.status = "failed"
            order.status = "failed"
            db.session.commit()
            return (
                jsonify(
                    {
                        "error": (
                            "Daraja STK is not fully configured. Add to .env: "
                            + ", ".join(missing)
                            + ". See docs/MPESA_SANDBOX.md (passkey + public HTTPS callback URL required)."
                        ),
                        "missing": missing,
                    }
                ),
                503,
            )
        payment.status = "paid"
        payment.mpesa_receipt = "DEV-MOCK-RECEIPT"
        _sync_order_payment_fields(order, payment)
        _finalize_paid_order(order, user_id)
        return jsonify(
            {
                "message": "Order placed (Daraja not configured — mock payment applied)",
                "order": order.to_dict(),
                "mock": True,
            }
        )

    mpesa = MpesaService()
    try:
        result = mpesa.stk_push(
            phone=normalized_phone,
            amount=float(order.total),
            account_reference=f"GH{order.id}",
            description=f"Order{order.id}",
        )
    except MpesaError as exc:
        payment.status = "failed"
        order.status = "failed"
        db.session.commit()
        return jsonify({"error": str(exc), "daraja": exc.details}), 502
    except Exception as exc:
        payment.status = "failed"
        order.status = "failed"
        db.session.commit()
        return jsonify({"error": f"M-Pesa request failed: {exc}"}), 502

    checkout_id = result.get("CheckoutRequestID")
    payment.checkout_request_id = checkout_id
    payment.status = "awaiting_payment"
    _sync_order_payment_fields(order, payment)
    db.session.commit()

    return jsonify(
        {
            "message": result.get("CustomerMessage", "STK push sent. Check your phone."),
            "checkout_request_id": checkout_id,
            "merchant_request_id": result.get("MerchantRequestID"),
            "order": order.to_dict(),
            "mock": False,
        }
    )


@payments_bp.post("/mpesa/callback")
def mpesa_callback():
    payload = request.get_json(silent=True) or {}
    body = payload.get("Body", {}).get("stkCallback", {})
    checkout_id = body.get("CheckoutRequestID")
    result_code = body.get("ResultCode")

    payment = Payment.query.filter_by(checkout_request_id=checkout_id).first()
    order = payment.order if payment else Order.query.filter_by(checkout_request_id=checkout_id).first()
    if not order:
        return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"})

    if not payment:
        payment = _create_payment(order, order.phone or "", status=order.status)

    if result_code == 0:
        metadata = body.get("CallbackMetadata", {}).get("Item", [])
        receipt = next((item.get("Value") for item in metadata if item.get("Name") == "MpesaReceiptNumber"), None)
        payment.status = "paid"
        payment.mpesa_receipt = receipt
        _sync_order_payment_fields(order, payment)
        _finalize_paid_order(order, order.user_id)
    else:
        payment.status = "failed"
        order.status = "failed"
        db.session.commit()

    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"})


@payments_bp.get("/mpesa/status/<int:order_id>")
@jwt_required()
def mpesa_order_status(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order.to_dict())


@payments_bp.post("/mpesa/query/<int:order_id>")
@jwt_required()
def mpesa_stk_query(order_id):
    """Poll Daraja STK status (useful when callback URL is not reachable)."""
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status in ("paid", "failed"):
        return jsonify(order.to_dict())

    checkout_id = order.checkout_request_id
    if not checkout_id:
        return jsonify({"error": "No STK checkout request for this order"}), 400

    if not MpesaService.is_configured():
        return jsonify(order.to_dict())

    mpesa = MpesaService()
    try:
        result = mpesa.stk_query(checkout_id)
    except MpesaError as exc:
        return jsonify({"error": str(exc), "order": order.to_dict(), "daraja": exc.details}), 502

    result_code = str(result.get("ResultCode", ""))
    payment = Payment.query.filter_by(checkout_request_id=checkout_id).first()

    if result_code == "0":
        if payment:
            payment.status = "paid"
            payment.mpesa_receipt = result.get("MpesaReceiptNumber") or payment.mpesa_receipt
            _sync_order_payment_fields(order, payment)
        else:
            order.status = "paid"
        _finalize_paid_order(order, user_id)
    elif result_code and result_code != "1037":
        if payment:
            payment.status = "failed"
        order.status = "failed"
        db.session.commit()

    db.session.refresh(order)
    return jsonify(
        {
            "order": order.to_dict(),
            "daraja": {
                "result_code": result.get("ResultCode"),
                "result_desc": result.get("ResultDesc"),
            },
        }
    )
