"""Safe SMTP configuration check. Sends no email."""
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)
for k in ["SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD", "EMAIL_FROM"]:
    v=(os.getenv(k) or "").strip().strip('"\'')
    print(f"{k}: {'SET' if v else 'MISSING'}")
print("No email was sent.")
