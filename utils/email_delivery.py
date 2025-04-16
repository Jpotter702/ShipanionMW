
import smtplib
from email.message import EmailMessage
from typing import Optional

def send_label_email(to_email: str, tracking_number: str, label_url: str, qr_code_url: Optional[str] = None):
    msg = EmailMessage()
    msg["Subject"] = f"Your Shipping Label – Tracking #{tracking_number}"
    msg["From"] = "no-reply@shipvox.ai"
    msg["To"] = to_email

    body = f"""
Hi there,

Here is your shipping label for tracking number {tracking_number}.

Label URL: {label_url}
"""
    if qr_code_url:
        body += f"QR Code: {qr_code_url}\n"

    body += "\nThanks for using ShipVox!"

    msg.set_content(body)

    # Stub only: In production, configure SMTP or email provider (SendGrid, SES, etc.)
    print(f"Email would be sent to {to_email} with subject: '{msg['Subject']}'")
