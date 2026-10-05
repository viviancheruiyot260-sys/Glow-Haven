import base64
from datetime import datetime

import requests

from config import Config


class MpesaError(Exception):
    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.details = details or {}


class MpesaService:
    SANDBOX_BASE = "https://sandbox.safaricom.co.ke"
    LIVE_BASE = "https://api.safaricom.co.ke"

    def __init__(self):
        self.base_url = self.SANDBOX_BASE if Config.MPESA_ENV == "sandbox" else self.LIVE_BASE

    @staticmethod
    def missing_config_keys() -> list[str]:
        missing = []
        if not Config.MPESA_CONSUMER_KEY:
            missing.append("MPESA_CONSUMER_KEY")
        if not Config.MPESA_CONSUMER_SECRET:
            missing.append("MPESA_CONSUMER_SECRET")
        if not Config.MPESA_PASSKEY:
            missing.append("MPESA_PASSKEY")
        if not Config.MPESA_SHORTCODE:
            missing.append("MPESA_SHORTCODE")
        if not Config.MPESA_CALLBACK_URL:
            missing.append("MPESA_CALLBACK_URL")
        return missing

    @classmethod
    def is_configured(cls) -> bool:
        return len(cls.missing_config_keys()) == 0

    def _oauth_token(self) -> str:
        if not Config.MPESA_CONSUMER_KEY or not Config.MPESA_CONSUMER_SECRET:
            raise MpesaError("M-Pesa consumer key and secret are required")

        auth = base64.b64encode(
            f"{Config.MPESA_CONSUMER_KEY}:{Config.MPESA_CONSUMER_SECRET}".encode()
        ).decode()
        response = requests.get(
            f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
            headers={"Authorization": f"Basic {auth}"},
            timeout=30,
        )
        try:
            data = response.json()
        except ValueError:
            data = {}
        if not response.ok:
            raise MpesaError(
                data.get("errorMessage") or f"OAuth failed (HTTP {response.status_code})",
                details=data,
            )
        token = data.get("access_token")
        if not token:
            raise MpesaError("OAuth response did not include access_token", details=data)
        return token

    def _password(self) -> tuple[str, str]:
        if not Config.MPESA_PASSKEY:
            raise MpesaError("M-Pesa passkey is required")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        data = f"{Config.MPESA_SHORTCODE}{Config.MPESA_PASSKEY}{timestamp}"
        password = base64.b64encode(data.encode()).decode()
        return password, timestamp

    @staticmethod
    def normalize_phone(phone: str) -> str:
        digits = "".join(ch for ch in phone if ch.isdigit())
        if digits.startswith("0"):
            digits = "254" + digits[1:]
        elif digits.startswith("7") or digits.startswith("1"):
            digits = "254" + digits
        elif not digits.startswith("254"):
            raise ValueError("Invalid Kenyan phone number")
        if len(digits) != 12:
            raise ValueError("Phone number must be a valid Kenyan MSISDN (2547XXXXXXXX)")
        return digits

    @staticmethod
    def _parse_daraja_response(response: requests.Response) -> dict:
        try:
            data = response.json()
        except ValueError as exc:
            raise MpesaError(f"Invalid JSON from Daraja (HTTP {response.status_code})") from exc

        if not response.ok:
            message = (
                data.get("errorMessage")
                or data.get("ResponseDescription")
                or f"Daraja request failed (HTTP {response.status_code})"
            )
            raise MpesaError(message, details=data)

        response_code = str(data.get("ResponseCode", "0"))
        if response_code != "0":
            raise MpesaError(
                data.get("ResponseDescription")
                or data.get("errorMessage")
                or "Daraja rejected the request",
                details=data,
            )
        return data

    def stk_push(self, phone: str, amount: float, account_reference: str, description: str) -> dict:
        if amount < 1:
            raise MpesaError("Amount must be at least 1 KES")

        token = self._oauth_token()
        password, timestamp = self._password()
        payload = {
            "BusinessShortCode": Config.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(round(amount)),
            "PartyA": phone,
            "PartyB": Config.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": Config.MPESA_CALLBACK_URL,
            "AccountReference": account_reference[:12],
            "TransactionDesc": description[:13],
        }
        response = requests.post(
            f"{self.base_url}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=30,
        )
        return self._parse_daraja_response(response)

    def stk_query(self, checkout_request_id: str) -> dict:
        token = self._oauth_token()
        password, timestamp = self._password()
        payload = {
            "BusinessShortCode": Config.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id,
        }
        response = requests.post(
            f"{self.base_url}/mpesa/stkpushquery/v1/query",
            json=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=30,
        )
        return self._parse_daraja_response(response)
