import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")


def send_challan_email(
    plate_no: str,
    fine_amount: int,
    helmet_violation: bool,
    triple_seat_violation: bool,
    phone_violation: bool,
    plate_img_path: str,
    full_img_path: str
):
    """
    Send traffic violation challan email with attachments.
    """

    if not SMTP_EMAIL or not SMTP_PASSWORD or not RECEIVER_EMAIL:
        print("[EMAIL ERROR] Missing SMTP credentials in .env")
        return

    violations = []

    if helmet_violation:
        violations.append("Helmet Violation")

    if triple_seat_violation:
        violations.append("Triple Seat Violation")

    if phone_violation:
        violations.append("Phone Usage Violation")

    violation_text = ", ".join(violations)

    subject = f"🚨 Traffic Challan Generated - {plate_no}"

    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    body = f"""
Dear Vehicle Owner,

A traffic violation has been detected for your vehicle.

Vehicle Number : {plate_no}
Violations     : {violation_text}
Fine Amount    : ₹{fine_amount}
Date & Time    : {time_now}

Please clear the challan through the official portal / RTO office.

Regards,
Traffic AI Monitoring System
"""

    msg = MIMEMultipart()
    msg["From"] = SMTP_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    # Attach Images
    for file_path in [plate_img_path, full_img_path]:
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())

                encoders.encode_base64(part)

                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{os.path.basename(file_path)}"'
                )

                msg.attach(part)

            except Exception as e:
                print(f"[EMAIL ATTACH ERROR] {file_path}: {e}")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"[EMAIL SENT] Challan sent for {plate_no}")

    except Exception as e:
        print("[EMAIL ERROR] Failed to send email:", e)