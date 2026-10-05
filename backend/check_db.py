"""Verify Glow Haven can connect to the configured database."""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import app  # noqa: E402
from db_startup import run_startup_diagnostics  # noqa: E402


def main() -> int:
    try:
        run_startup_diagnostics(app)
    except RuntimeError as exc:
        print(f"[FAIL] {exc}")
        return 1
    import sys

    ok_prefix = "✓" if "utf" in (sys.stdout.encoding or "").lower() else "[OK]"
    print(f"{ok_prefix} Database check complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
