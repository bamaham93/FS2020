from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class PrayerProfile(models.Model):
    """
    Extends the Django User in ways that are specific to the prayer requests app.
    """

    user = models.OneToOneField(User, models.CASCADE)


class Person(models.Model):
    """
    A person that may be contacted for the prayer requests contact chain.
    """

    user = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="prayer_person",
        help_text="Optional Django user account associated with this person.",
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    sms_consent = models.BooleanField(
        default=False, help_text="User has consented to receive SMS messages"
    )
    sms_consent_date = models.DateTimeField(
        null=True, blank=True, help_text="Date and time when SMS consent was given"
    )
    notify_on_inbound_sms = models.BooleanField(
        default=True,
        help_text="Send an SMS alert when a new inbound Prayer message arrives.",
    )

    def __str__(self):
        """ """
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "People"


class PrayerGroup(models.Model):
    """
    Pre-assembled group of people that can be contacted, such as membership roll,
    """

    name = models.CharField(max_length=50)
    short_description = models.CharField(max_length=100)
    long_description = models.TextField(blank=True, null=True)
    people = models.ManyToManyField(Person)

    def __str__(self):
        """ """
        return f"{self.name}"


class PrayerMessage(models.Model):
    """ """

    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    submitted_by = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="prayer_requests",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_important = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    answer_text = models.TextField(null=True, blank=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    groups = models.ManyToManyField(
        PrayerGroup,
        blank=True,
        related_name="messages",
        help_text="Groups this message is targeted to",
    )
    direct_recipients = models.ManyToManyField(
        Person,
        blank=True,
        related_name="direct_messages",
        help_text="One-off contacts this message is targeted to",
    )

    def __str__(self):
        return f"{self.name}"


class SMSLog(models.Model):
    """
    Records every individual SMS send attempt so that successes and
    failures can be reviewed later.
    """

    message = models.ForeignKey(
        PrayerMessage,
        on_delete=models.CASCADE,
        related_name="sms_logs",
    )
    recipient = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sms_logs",
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    error_message = models.TextField(blank=True, default="")
    sent_by = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sms_sends",
    )

    def __str__(self):
        status = "OK" if self.success else "FAIL"
        recipient_str = str(self.recipient) if self.recipient else "unknown"
        return f"[{status}] {self.message} → {recipient_str}"

    class Meta:
        verbose_name = "SMS Log"
        verbose_name_plural = "SMS Logs"
        ordering = ["-sent_at"]


class InboundSmsMessage(models.Model):
    provider = models.CharField(max_length=30, default="twilio")
    provider_message_id = models.CharField(max_length=64, unique=True)

    from_number = models.CharField(max_length=20)
    to_number = models.CharField(max_length=20)

    body = models.TextField(blank=True)
    received_at = models.DateTimeField(auto_now_add=True)

    person = models.ForeignKey(
        Person,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="inbound_sms_messages",
    )

    read_by = models.ManyToManyField(
        User,
        blank=True,
        related_name="read_inbound_sms_messages",
        help_text="Prayer administrators who have marked this message as read.",
    )

    direction = models.CharField(max_length=20, default="inbound")
    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-received_at"]

    @property
    def sender_display(self):
        if self.person:
            return f"{self.person.first_name} {self.person.last_name}".strip()
        return self.from_number

    @property
    def notification_summary(self):
        body = self.body.strip() if self.body else "(no message body)"
        return f"You have a message from {self.sender_display}: {body}"

    def __str__(self):
        return self.notification_summary


class Permissions(models.Model):
    profile = models.OneToOneField(PrayerProfile, on_delete=models.CASCADE)
    may_send_emails = models.BooleanField()
    may_send_sms = models.BooleanField()
