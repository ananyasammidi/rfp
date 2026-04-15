"""
Gmail SMTP used for sending emails to distributors
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta


GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_PASS = os.getenv("GMAIL_APP_PASS", "")


def _build_body(
    distributor_name: str,
    restaurant: str,
    ingredients: list[dict],
    deadline: str,
) -> tuple[str, str]:

    ing_lines = "\n".join(
        f"  - {i['normalized_name'].title()}"
        for i in ingredients
    )

    subject = (
        f"RFP – Ingredient Quote Request from {restaurant} | "
        f"Response Deadline {deadline}"
    )

    body = f"""Dear {distributor_name} Team,

I'm reaching out on behalf of the {restaurant} team. {restaurant} is requesting sourcing information for ingredients.

We are requesting a price quote for these ingredients and quantities:

{ing_lines}

Please get back to us with your quoted prices per unit by {deadline}.

Thank you for your time!

Best regards,
{restaurant} Team"""

    return subject, body


def send_rfp(
    to_address: str,
    distributor_name: str,
    restaurant: str,
    ingredients: list[dict],
) -> tuple[str, str, str | None]:
    deadline = (datetime.now() + timedelta(days=7)).strftime("%B %d, %Y")
    subject, body = _build_body(distributor_name, restaurant, ingredients, deadline)

    if not GMAIL_USER or not GMAIL_PASS:
        print(f"\n[MOCK EMAIL] To: {to_address}")
        print(f"Subject: {subject}")
        print(body[:300] + "...\n")
        return subject, body, "mock: GMAIL_USER / GMAIL_APP_PASS not configured"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = GMAIL_USER
        msg["To"] = to_address
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, to_address, msg.as_string())

        return subject, body, None

    except Exception as exc:
        return subject, body, str(exc)
