import logging
from dataclasses import dataclass

from django.utils import timezone

from prayer.models import Person, InboundSmsMessage

logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client as TwilioClient
    from twilio.base.exceptions import TwilioRestException

    try:
        from credentials.twilio import (
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN,
            TWILIO_PHONE_NUMBER,
        )
    except ModuleNotFoundError:
        from credentials.mock_faa_twilio import (
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN,
            TWILIO_PHONE_NUMBER,
        )
    _TWILIO_AVAILABLE = True
except ImportError:
    _TWILIO_AVAILABLE = False
    TwilioClient = None
    TwilioRestException = Exception
    TWILIO_ACCOUNT_SID = ""
    TWILIO_AUTH_TOKEN = ""
    TWILIO_PHONE_NUMBER = ""


@dataclass(frozen=True)
class InboundSmsPayload:
    provider: str
    provider_message_id: str
    from_number: str
    to_number: str
    body: str


def _normalize_phone_number(phone_number: str) -> str:
    return "".join(character for character in phone_number if character.isdigit())[-10:]


def _match_person(from_number: str) -> Person | None:
    incoming_number = _normalize_phone_number(from_number)

    for person in Person.objects.exclude(phone_number__isnull=True).exclude(
        phone_number=""
    ):
        if _normalize_phone_number(person.phone_number) == incoming_number:
            return person

    return None


def _notify_admins(message: InboundSmsMessage) -> None:
    """
    Send an SMS notification to all Prayer Group admins when a new inbound
    message is received.

    The notification reads:
        "A message was received at {time} on {date} from {name or phone number}."
    """
    admins = list(
        Person.objects.filter(is_admin=True)
        .exclude(phone_number__isnull=True)
        .exclude(phone_number="")
    )
    if not admins:
        return

    if not _TWILIO_AVAILABLE:
        logger.warning("Admin notification skipped: Twilio library is not available.")
        return

    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
        logger.warning(
            "Admin notification skipped: Twilio credentials are not configured."
        )
        return

    received_at = message.received_at or timezone.now()
    time_str = received_at.strftime("%-I:%M %p")
    date_str = received_at.strftime("%B %-d, %Y")

    if message.person:
        sender = f"{message.person.first_name} {message.person.last_name}".strip()
    else:
        sender = message.from_number

    notification = f"A message was received at {time_str} on {date_str} from {sender}."

    client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    for admin in admins:
        try:
            client.messages.create(
                body=notification,
                from_=TWILIO_PHONE_NUMBER,
                to=admin.phone_number,
            )
            logger.info(
                "Admin notification sent to %s %s.",
                admin.first_name,
                admin.last_name,
            )
        except TwilioRestException as exc:
            logger.warning(
                "Failed to send admin notification to %s %s: %s",
                admin.first_name,
                admin.last_name,
                exc,
            )


def handle_inbound_sms(payload: InboundSmsPayload) -> InboundSmsMessage:
    message, created = InboundSmsMessage.objects.get_or_create(
        provider_message_id=payload.provider_message_id,
        defaults={
            "provider": payload.provider,
            "from_number": payload.from_number,
            "to_number": payload.to_number,
            "body": payload.body,
            "person": _match_person(payload.from_number),
        },
    )

    if created:
        _notify_admins(message)
        return message

    if not message.person:
        message.person = _match_person(payload.from_number)
        if message.person:
            message.save(update_fields=["person"])

    return message
