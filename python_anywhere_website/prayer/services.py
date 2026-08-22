import logging
from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q

from prayer.models import Person, InboundSmsMessage

logger = logging.getLogger(__name__)

PRAYER_MANAGER_GROUP = "Prayer Manager"
PRAYER_APP_URL = "https://jacob-mcgowin.us/prayer/"
TWILIO_CONTROL_MESSAGES = {
    "STOP",
    "STOPALL",
    "UNSUBSCRIBE",
    "CANCEL",
    "END",
    "QUIT",
    "START",
    "YES",
    "UNSTOP",
    "HELP",
    "INFO",
}

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


def _is_twilio_control_message(body: str) -> bool:
    return str(body or "").strip().upper() in TWILIO_CONTROL_MESSAGES


def _get_prayer_admin_persons() -> list[Person]:
    """
    Return consented Person records linked to Prayer Managers or staff users.

    The explicit User-to-Person relationship is authoritative. Matching by name
    is limited to the one-time data migration that introduced this behavior.
    """
    eligible_users = User.objects.filter(
        Q(groups__name=PRAYER_MANAGER_GROUP) | Q(is_staff=True)
    ).distinct()
    return list(
        Person.objects.filter(
            user__in=eligible_users,
            sms_consent=True,
            notify_on_inbound_sms=True,
        )
        .select_related("user")
        .exclude(phone_number__isnull=True)
        .exclude(phone_number="")
        .distinct()
    )


def _notification_cooldown_active(message: InboundSmsMessage) -> bool:
    """Return whether an optional global inbound-alert cooldown is active."""
    try:
        cooldown_minutes = int(
            getattr(settings, "INBOUND_SMS_ADMIN_COOLDOWN_MINUTES", 0)
        )
    except (TypeError, ValueError):
        cooldown_minutes = 0

    if cooldown_minutes <= 0:
        return False

    cutoff = message.received_at - timedelta(minutes=cooldown_minutes)
    return InboundSmsMessage.objects.exclude(pk=message.pk).filter(
        received_at__gte=cutoff,
        received_at__lt=message.received_at,
    ).exists()


def _notify_admins(message: InboundSmsMessage) -> None:
    """
    Send an SMS notification to all Prayer Group admins when a new inbound
    message is received.

    Recipients are the union of the 'Prayer Manager' group and staff users.
    Each recipient must have a linked Person record, a phone number, SMS
    consent, and inbound notifications enabled.
    """
    if _notification_cooldown_active(message):
        logger.info("Admin notification skipped because cooldown is active.")
        return

    admins = _get_prayer_admin_persons()
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

    if message.person:
        sender = f"{message.person.first_name} {message.person.last_name}".strip()
    else:
        sender = message.from_number

    notification = (
        f"New Message from {sender}: {message.body}\n\n"
        f"Log into {PRAYER_APP_URL} to see more."
    )

    try:
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except Exception:
        logger.exception("Failed to initialize Twilio admin notification client.")
        return

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
        except Exception:
            logger.exception(
                "Unexpected failure sending admin notification to %s %s.",
                admin.first_name,
                admin.last_name,
            )


def handle_inbound_sms(payload: InboundSmsPayload) -> InboundSmsMessage | None:
    if _is_twilio_control_message(payload.body):
        logger.info("Twilio control message ignored for Prayer inbox.")
        return None

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
        try:
            _notify_admins(message)
        except Exception:
            # The inbound message is the source of truth. Notification failures
            # must not make Twilio retry an otherwise successful ingestion.
            logger.exception(
                "Unexpected admin notification failure for inbound message %s.",
                message.provider_message_id,
            )
        return message

    if not message.person:
        message.person = _match_person(payload.from_number)
        if message.person:
            message.save(update_fields=["person"])

    return message
