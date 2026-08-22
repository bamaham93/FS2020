from prayer.models import InboundSmsMessage
from prayer.permissions import can_view_inbound_sms


def inbound_sms_notifications(request):
    if not request.path.startswith("/prayer/"):
        return {}

    user = getattr(request, "user", None)
    if not can_view_inbound_sms(user):
        return {}

    unread_messages = InboundSmsMessage.objects.select_related("person").exclude(
        read_by=user
    )
    return {
        "inbound_sms_can_view": True,
        "inbound_sms_notifications": unread_messages[:5],
        "inbound_sms_unread_count": unread_messages.count(),
    }
