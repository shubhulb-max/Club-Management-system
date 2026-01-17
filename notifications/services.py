import logging
from typing import Optional

from django.conf import settings
from django.utils import timezone

try:
    from twilio.base.exceptions import TwilioRestException
    from twilio.rest import Client
except ImportError:  # pragma: no cover - optional dependency
    TwilioRestException = Exception
    Client = None

logger = logging.getLogger(__name__)


def _get_twilio_client() -> Optional[Client]:
    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)

    if not Client or not (account_sid and auth_token):
        logger.warning("Twilio credentials missing; WhatsApp message skipped.")
        return None

    try:
        return Client(account_sid, auth_token)
    except Exception:  # pragma: no cover - defensive logging
        logger.exception("Failed to instantiate Twilio client.")
        return None


def _format_whatsapp_number(phone_number: str) -> Optional[str]:
    if not phone_number:
        return None

    sanitized = phone_number.strip().replace(" ", "")
    if sanitized.startswith("whatsapp:"):
        return sanitized
    # Twilio requires e.g. whatsapp:+911234567890
    if not sanitized.startswith("+"):
        logger.warning("Phone number %s missing country code.", phone_number)
        return None
    return f"whatsapp:{sanitized}"


def send_whatsapp_message(phone_number: str, body: str) -> bool:
    """
    Sends a WhatsApp message via Twilio. Returns True if queued successfully.
    """
    client = _get_twilio_client()
    from_number = getattr(settings, "TWILIO_WHATSAPP_NUMBER", None)
    if not client or not from_number:
        logger.warning("Twilio WhatsApp configuration missing; message skipped.")
        return False

    to_number = _format_whatsapp_number(phone_number)
    if not to_number:
        logger.warning("Invalid WhatsApp recipient; message skipped.")
        return False

    try:
        client.messages.create(
            body=body,
            from_=from_number,
            to=to_number,
        )
        return True
    except TwilioRestException:
        logger.exception("Failed to send WhatsApp message to %s", to_number)
        return False


def notify_player_onboarding(player) -> bool:
    if not player.phone_number:
        return False
    body = (
        f"Welcome to the club, {player.first_name}! "
        "Your membership and subscription are now active. "
        "Admission invoice will appear in your account shortly."
    )
    return send_whatsapp_message(player.phone_number, body)


def notify_payment_received(transaction) -> bool:
    player = transaction.player
    if not player.phone_number:
        return False
    paid_on = transaction.payment_date or timezone.localdate()
    body = (
        f"Hi {player.first_name}, we received your payment of ₹{transaction.amount} "
        f"for {transaction.get_category_display()} on {paid_on}. Thank you!"
    )
    return send_whatsapp_message(player.phone_number, body)
