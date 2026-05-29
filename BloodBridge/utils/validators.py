import re
from datetime import date, datetime

from email_validator import EmailNotValidError, validate_email


BLOOD_GROUPS = ("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-")
URGENCY_LEVELS = ("Low", "Medium", "High", "Critical")


def valid_email(email):
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def valid_phone(phone):
    return bool(re.fullmatch(r"[0-9+\-\s]{7,20}", phone or ""))


def parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def donor_eligibility(last_donation_date):
    """A donor is usually eligible after 90 days from the last donation."""
    if not last_donation_date:
        return "Eligible"
    if isinstance(last_donation_date, str):
        last_donation_date = parse_date(last_donation_date)
    days_since = (date.today() - last_donation_date).days
    return "Eligible" if days_since >= 90 else "Not Eligible"

