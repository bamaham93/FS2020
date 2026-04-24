from dataclasses import dataclass

from prayer.models import Person, InboundSmsMessage


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


def handle_inbound_sms(payload: InboundSmsPayload) -> InboundSmsMessage:
    message, created = InboundSmsMessage.objects.get_or_create(
        provider=payload.provider,
        provider_message_id=payload.provider_message_id,
        defaults={
            "from_number": payload.from_number,
            "to_number": payload.to_number,
            "body": payload.body,
            "person": _match_person(payload.from_number),
        },
    )

    if created:
        return message

    if not message.person:
        message.person = _match_person(payload.from_number)
        if message.person:
            message.save(update_fields=["person"])

    return message
