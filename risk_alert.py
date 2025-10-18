# risk_alert.py
import smtplib
from email.message import EmailMessage
import os

RISK_KEYWORDS = ["suicide", "killing myself",
                 "end my life", "hurt myself", "kill myself"]


def check_for_risk(text):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in RISK_KEYWORDS)


def send_risk_email(alert_text, therapist_email="sanaabdulrehman286@gmail.com"):
    try:
        EMAIL_ADDRESS = os.getenv("THERAPY_APP_EMAIL")
        EMAIL_PASSWORD = os.getenv("THERAPY_APP_PASSWORD")

        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            raise ValueError(
                "Email credentials not found in environment variables.")

        msg = EmailMessage()
        msg.set_content(
            f"🚨 Risk Alert 🚨\n\nDetected a message:\n\n\"{alert_text}\", Please review the session for further evaluation and take appropriate action if needed.")
        msg["Subject"] = "⚠️ Urgent: Risk Word Detected in User Message"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = therapist_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print("Error sending risk email:", str(e))
