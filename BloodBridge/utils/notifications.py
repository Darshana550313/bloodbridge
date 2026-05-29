from flask import current_app


def send_email_notification(to_email, subject, body):
    """Log email notifications when SMTP is not configured; send-ready hook for production."""
    if not current_app.config.get("MAIL_SERVER"):
        current_app.logger.info("Email notification to %s: %s - %s", to_email, subject, body)
        return True

    # Keep the implementation dependency-light for beginners. In production,
    # connect smtplib here or replace this function with AWS SES integration.
    current_app.logger.info("SMTP configured. Email queued to %s: %s", to_email, subject)
    return True


def send_sms_alert(phone, message):
    """SMS placeholder that can be replaced with AWS SNS or Twilio."""
    current_app.logger.info("SMS alert to %s: %s", phone, message)
    return True

