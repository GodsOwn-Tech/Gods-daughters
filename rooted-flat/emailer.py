"""
emailer.py — sends the password reset code by email.

If SMTP isn't configured in .env, this falls back to printing the email to
the terminal instead of failing — so password reset still works while
you're developing locally, without needing to set up a real mailbox first.

To send real emails, fill in SMTP_HOST / SMTP_PORT / SMTP_USER /
SMTP_PASSWORD in .env. Most providers (Gmail, Outlook, etc.) require an
"app password" rather than your normal login password for this — check
your provider's docs for "SMTP app password".
"""
import os
import smtplib
from email.mime.text import MIMEText


def send_email(to_email, subject, body):
    host = os.environ.get("SMTP_HOST")
    port = os.environ.get("SMTP_PORT", "587")
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASSWORD")
    from_addr = os.environ.get("SMTP_FROM") or user

    if not host or not user or not password:
        print("\n" + "=" * 60)
        print(f"[DEV MODE — no SMTP configured] Would have emailed {to_email}:")
        print(f"Subject: {subject}")
        print(body)
        print("=" * 60 + "\n")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email

    with smtplib.SMTP(host, int(port)) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(from_addr, [to_email], msg.as_string())
