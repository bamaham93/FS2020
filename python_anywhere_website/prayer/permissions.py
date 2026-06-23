PRAYER_ADMINS_GROUP = "Prayer Admins"


def can_view_inbound_sms(user):
    if not user or not user.is_authenticated:
        return False

    if user.is_staff or user.is_superuser:
        return True

    return user.groups.filter(name=PRAYER_ADMINS_GROUP).exists()
