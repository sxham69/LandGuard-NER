import os
import re
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"), override=False)
except Exception:
    pass

def _clean(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().strip("\"'").strip()

def _config():
    return {
        "host": _clean(os.getenv("SMTP_HOST", "smtp.gmail.com")),
        "port": int(_clean(os.getenv("SMTP_PORT", "587")) or "587"),
        "username": _clean(os.getenv("SMTP_USERNAME")),
        "password": _clean(os.getenv("SMTP_PASSWORD")),
        "from_email": _clean(os.getenv("EMAIL_FROM")) or _clean(os.getenv("SMTP_USERNAME")),
        "use_tls": _clean(os.getenv("SMTP_USE_TLS", "true")).lower() not in ("0", "false", "no"),
    }

def _looks_placeholder(value: str) -> bool:
    if not value:
        return True
    lowered = value.lower()
    return any(x in lowered for x in ("your_", "replace_me", "example.com", "your-app-password"))

def _friendly_email_error(exc: Exception) -> str:
    text = re.sub(r"\x1b\[[0-9;]*m", "", str(exc))
    low = text.lower()
    if "authentication" in low or "auth" in low or "535" in low:
        return "Email authentication failed. For Gmail, use your full Gmail address and a Google App Password (not your normal account password)."
    if "connection" in low or "timed out" in low:
        return "Could not connect to the SMTP server. Check SMTP_HOST/SMTP_PORT and your internet connection."
    return text

def send_email(to_email: str, subject: str, message: str) -> dict:
    cfg = _config()
    to_email = str(to_email).strip()
    subject = str(subject).strip() or "LandslideGuard NER Alert"
    message = str(message).strip()
    if not to_email or "@" not in to_email:
        return {"status": "FAILED", "provider": "SMTP", "to": to_email, "error": "Enter a valid recipient email address."}
    if _looks_placeholder(cfg["username"]) or _looks_placeholder(cfg["password"]):
        return {"status": "FAILED", "provider": "SMTP", "to": to_email,
                "error": "Email configuration is missing. Set SMTP_USERNAME and SMTP_PASSWORD in .env."}
    try:
        msg = EmailMessage()
        msg["From"] = cfg["from_email"]
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(message)
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=10) as server:
            if cfg["use_tls"]:
                server.starttls()
            server.login(cfg["username"], cfg["password"])
            server.send_message(msg)
        return {"status": "SENT", "provider": "SMTP", "to": to_email,
                "sent_at": datetime.now(timezone.utc).isoformat()}
    except Exception as exc:
        return {"status": "FAILED", "provider": "SMTP", "to": to_email, "error": _friendly_email_error(exc)}

def dispatch_email(subject: str, message: str, recipients: list) -> dict:
    results = [send_email(str(email).strip(), subject, message) for email in recipients if str(email).strip()]
    sent = sum(1 for r in results if r.get("status") == "SENT")
    failed = sum(1 for r in results if r.get("status") == "FAILED")
    if sent and not failed:
        status = "sent"
    elif sent:
        status = "partial"
    elif failed:
        status = "failed"
    else:
        status = "disabled"
    return {"status": status, "sent": sent, "failed": failed, "detail": results}

def mobile_push_status(enabled: bool) -> str:
    return "SIMULATED" if enabled else "disabled"
