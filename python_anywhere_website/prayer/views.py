import logging
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from twilio.request_validator import RequestValidator
from urllib.parse import urlsplit, urlunsplit

# from logic.users_groups import is_group
from prayer.forms import (
    NewGroupForm,
    NewPersonForm,
    NewMessageForm,
    PermissionsForm,
    PublicSignupForm,
)
from prayer.models import Person, PrayerGroup, PrayerMessage, SMSLog, InboundSmsMessage
from prayer.services import InboundSmsPayload, handle_inbound_sms

try:
    import logic.queries
    from logic.Messaging.sms import SMSMessage
    from logic.queries import PrayerGroupQueries, PrayerMessageQueries
except ModuleNotFoundError:
    pass

# from django.contrib.messages import get_messages


def is_group(user, group):
    if user.groups.filter(name=group):
        return True
    else:
        return False


logger = logging.getLogger(__name__)


# Create your views here.
def index(request) -> render:
    """
    Home page for prayer app.
    """
    context = {}
    return render(request, "prayer/index.html", context)


@login_required()
@staff_member_required
def new_message(request) -> render:
    """
    Create a new message, then continue in the message detail workflow.
    Staff-only view for composing messages to prayer groups.
    """
    context = {"form": NewMessageForm()}
    if request.method == "POST":
        form = NewMessageForm(request.POST)
        if form.is_valid():
            message = form.save()
            messages.success(request, "Your message was saved!")
            return redirect("prayer:message-detail", id=message.id)
        else:
            context["form"] = form
            messages.warning(request, "There was a problem with your submission.")
    return render(request, "prayer/new_message.html", context)


@login_required()
@staff_member_required
def message_detail(request, id):
    """
    See message details and send to prayer groups.
    Persists an SMSLog entry for every send attempt (success or failure).
    """
    # Check if logic.queries classes are available
    if "PrayerMessageQueries" in globals() and "PrayerGroupQueries" in globals():
        try:
            pm_queries = PrayerMessageQueries()
            message = pm_queries.get_message_by_id(id=id)
            pg_queries = PrayerGroupQueries()
            prayer_groups = pg_queries.get_all()
        except (AttributeError, ImportError):
            message = PrayerMessage.objects.get(id=id)
            prayer_groups = PrayerGroup.objects.all()
            pg_queries = None
    else:
        message = PrayerMessage.objects.get(id=id)
        prayer_groups = PrayerGroup.objects.all()
        pg_queries = None

    sms_logs = SMSLog.objects.filter(message=message).select_related(
        "recipient", "sent_by"
    )
    # IDs of groups already associated with this message (for pre-checking boxes)
    associated_group_ids = set(message.groups.values_list("id", flat=True))

    context = {
        "message": message,
        "prayer_groups": prayer_groups,
        "sms_logs": sms_logs,
        "associated_group_ids": associated_group_ids,
    }

    # Send messages
    if request.method == "POST":
        checks = request.POST.getlist("groups")

        people_set = set()

        for group_name in checks:
            try:
                group_ = (
                    pg_queries.get_group_members(group_name)
                    if pg_queries is not None
                    else PrayerGroup.objects.get(name=group_name).people.all()
                )
            except (AttributeError, ImportError):
                group_ = PrayerGroup.objects.get(name=group_name).people.all()
            people_set.update(group_)

        # Persist the group selection on the message
        selected_groups = PrayerGroup.objects.filter(name__in=checks)
        message.groups.set(selected_groups)

        # Filter to only people who have consented to SMS and have a phone number
        consented_people = set(
            Person.objects.filter(
                id__in=[p.id for p in people_set],
                sms_consent=True,
                phone_number__isnull=False,
            ).exclude(phone_number="")
        )

        if consented_people:
            if "SMSMessage" in globals():
                try:
                    sms_message = SMSMessage(
                        body=message.message, contacts=consented_people, testing=False
                    )
                    results = sms_message.send()
                    success_count = 0
                    for person, (success, error) in results.items():
                        SMSLog.objects.create(
                            message=message,
                            recipient=person,
                            success=success,
                            error_message=error,
                            sent_by=request.user,
                        )
                        if success:
                            success_count += 1
                    fail_count = len(results) - success_count
                    if fail_count:
                        messages.warning(
                            request,
                            f"Message sent to {success_count} recipient(s). "
                            f"{fail_count} send(s) failed — see log for details.",
                        )
                    else:
                        messages.success(
                            request,
                            f"Message sent to {success_count} recipient(s) who have consented to SMS.",
                        )
                except (AttributeError, ImportError) as e:
                    messages.error(request, f"Failed to send SMS messages: {e}")
            else:
                messages.warning(request, "SMS functionality is not available.")
        else:
            messages.warning(
                request, "No recipients with SMS consent found in the selected groups."
            )

        return redirect("prayer:message-detail", id=id)

    return render(request, "prayer/message_detail.html", context)


@login_required()
@staff_member_required
def send_message(request, id: int):
    """
    Redirects to message_detail, which handles sending.
    Kept for URL compatibility.
    """
    return redirect("prayer:message-detail", id=id)


@login_required()
@staff_member_required
def groups(request) -> render:
    """
    List of groups.
    Staff-only view for creating and managing prayer groups.
    """
    context = {"new_group_form": NewGroupForm(), "groups": PrayerGroup.objects.all()}

    if request.method == "POST":
        form = NewGroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "You've successfully created a new group.")
    return render(request, "prayer/groups.html", context)


@login_required()
def group(request, group_id):
    """
    Group detail page, user editable.
    """
    group_ = PrayerGroup.objects.get(id=group_id)

    # Get group membership
    if "PrayerGroupQueries" in globals():
        try:
            membership = PrayerGroupQueries()
            group_membership = membership.get_group_members(group=group_.name)
        except (AttributeError, ImportError):
            group_membership = group_.people.all()
    else:
        group_membership = group_.people.all()

    context = {
        "group": group_,
        "form": NewGroupForm(PrayerGroup.objects.get(id=group_id).__dict__),
        "group_membership": group_membership,
    }
    if request.method == "POST":
        # Takes new data from form, applies it to instance to overwrite prev data
        form = NewGroupForm(request.POST, instance=group_)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"You've successfully edited the group {group_.name}"
            )
    return render(request, "prayer/group.html", context)


@login_required()
def delete_group(request, group_id):
    """
    Delete the group with id of group_id.
    """
    group_ = PrayerGroup.objects.get(id=group_id)  # TODO Move to logic/queries.py
    group_.delete()
    messages.success(request, f"You've successfully deleted the {group_.name} group.")
    return redirect("prayer:groups")


@login_required()
def prayer_requests(request) -> render:
    """
    List of prayer requests.
    """
    from prayer.forms import NewPrayerRequestForm

    form = NewPrayerRequestForm()
    if request.method == "POST":
        form = NewPrayerRequestForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            # Use authenticated user's name for the request
            user = request.user
            if user.first_name or user.last_name:
                instance.name = f"{user.first_name} {user.last_name}".strip()
            else:
                instance.name = user.username
            instance.save()
            messages.success(request, "Your prayer request was submitted.")
            return redirect("prayer:prayer_requests")
        else:
            messages.warning(request, "There was a problem with your submission.")

    # Determine which requests to show: staff see all, others see their own
    if request.user.is_staff:
        requests_qs = PrayerMessage.objects.all().order_by("-id")
    else:
        requests_qs = PrayerMessage.objects.filter(submitted_by=request.user).order_by(
            "-id"
        )

    context = {"form": form, "prayer_requests": requests_qs}
    return render(request, "prayer/prayer_request.html", context)


@login_required()
def delete_prayer_request(request, id: int):
    if not request.user.is_staff:
        messages.error(request, "Not authorized.")
        return redirect("prayer:prayer_requests")
    try:
        pm = PrayerMessage.objects.get(id=id)
        pm.delete()
        messages.success(request, "Prayer request deleted.")
    except PrayerMessage.DoesNotExist:
        messages.warning(request, "Prayer request not found.")
    return redirect("prayer:prayer_requests")


@login_required()
def toggle_important(request, id: int):
    if not request.user.is_staff:
        messages.error(request, "Not authorized.")
        return redirect("prayer:prayer_requests")
    try:
        pm = PrayerMessage.objects.get(id=id)
        pm.is_important = not pm.is_important
        pm.save()
        messages.success(request, "Prayer request importance toggled.")
    except PrayerMessage.DoesNotExist:
        messages.warning(request, "Prayer request not found.")
    return redirect("prayer:prayer_requests")


@login_required()
def toggle_complete(request, id: int):
    if not request.user.is_staff:
        messages.error(request, "Not authorized.")
        return redirect("prayer:prayer_requests")
    try:
        pm = PrayerMessage.objects.get(id=id)
        pm.is_completed = not pm.is_completed
        pm.save()
        messages.success(request, "Prayer request completion toggled.")
    except PrayerMessage.DoesNotExist:
        messages.warning(request, "Prayer request not found.")
    return redirect("prayer:prayer_requests")


@login_required()
def answer_prayer_request(request, id: int):
    if not request.user.is_staff:
        messages.error(request, "Not authorized.")
        return redirect("prayer:prayer_requests")
    if request.method == "POST":
        answer = request.POST.get("answer", "").strip()
        try:
            pm = PrayerMessage.objects.get(id=id)
            pm.answer_text = answer
            pm.answered_at = timezone.now()
            pm.save()
            messages.success(request, "Saved answer to prayer request.")
        except PrayerMessage.DoesNotExist:
            messages.warning(request, "Prayer request not found.")
    return redirect("prayer:prayer_requests")


@login_required()
def people(request) -> render:
    """
    List of people.
    """
    context = {
        "new_person_form": NewPersonForm(),
        "people_list": None,
        # 'messages': get_messages(request)
    }

    if request.user.is_staff:
        context["people_list"] = Person.objects.all()

    if request.method == "POST":
        form = NewPersonForm(request.POST)
        if form.is_valid():
            person = form.save(commit=False)
            # Set consent date if consent is given
            if person.sms_consent and not person.sms_consent_date:
                person.sms_consent_date = timezone.now()
            person.save()
            messages.success(request, "Your submission was saved!")
        else:
            context["new_person_form"] = NewPersonForm(request.POST)
            messages.warning(request, "There was a problem saving your form.")
    return render(request, "prayer/prayer-people.html", context)


@login_required()
def delete_person(request, person_id: int) -> redirect:
    """ """
    person = Person.objects.get(id=person_id)
    person.delete()
    messages.success(
        request, f"You have successfully deleted {person.first_name} {person.last_name}"
    )
    return redirect("prayer:people")


@login_required()
def permissions(request, id: int):
    context = {"form": PermissionsForm()}
    return render(request, "prayer/permissions.html", context)


def public_signup(request) -> render:
    """
    Public signup form for people to opt-in to receive SMS messages.
    Does not require login - anyone can sign up.
    """
    context = {
        "signup_form": PublicSignupForm(),
    }

    if not request.user.is_authenticated:
        if request.method == "POST":
            messages.warning(
                request,
                "Please sign up for an account and log in before joining SMS prayer updates.",
            )
        return render(request, "prayer/public_signup.html", context)

    if request.method == "POST":
        form = PublicSignupForm(request.POST)
        if form.is_valid():
            person = form.save(commit=False)
            # Automatically set SMS consent to True for public signups
            person.sms_consent = True
            person.sms_consent_date = timezone.now()
            person.save()
            messages.success(
                request,
                "Thank you for signing up! You'll now receive prayer updates via SMS. "
                "Reply STOP at any time to unsubscribe.",
            )
            # Redirect to prevent resubmission
            return redirect("prayer:public_signup")
        else:
            context["signup_form"] = form
            messages.warning(
                request,
                "There was a problem with your submission. Please check the form.",
            )

    return render(request, "prayer/public_signup.html", context)


def _is_valid_twilio_signature(request) -> bool:
    signature = request.META.get("HTTP_X_TWILIO_SIGNATURE")
    if not signature:
        logger.warning("Twilio webhook rejected: missing X-Twilio-Signature header")
        return False

    twilio_token = _get_twilio_auth_token()
    if not twilio_token:
        logger.error("Twilio webhook rejected: TWILIO_AUTH_TOKEN is not configured")
        return False

    validator = RequestValidator(twilio_token)

    candidate_urls = _twilio_signature_candidate_urls(request)
    for url in candidate_urls:
        if validator.validate(url, request.POST, signature):
            return True
    logger.warning(
        "Twilio webhook rejected: signature validation failed for all %s candidate URLs",
        len(candidate_urls),
    )
    return False


def _get_twilio_auth_token() -> str:
    """
    Read Twilio auth token from supported config locations.
    """
    settings_token = str(getattr(settings, "TWILIO_AUTH_TOKEN", "")).strip()
    if settings_token:
        return settings_token

    env_token = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
    if env_token:
        return env_token

    # Legacy fallback used elsewhere in this project for outbound SMS.
    try:
        from logic.Messaging.sms import TWILIO_AUTH_TOKEN as legacy_token
    except Exception:
        legacy_token = ""
    return str(legacy_token).strip()


def _twilio_signature_candidate_urls(request):
    """
    Return candidate absolute URLs for Twilio signature validation.

    Twilio signs the exact webhook URL (including scheme). Some reverse proxies
    can forward requests to Django as plain HTTP even when the public URL is
    HTTPS, so we try both variants.
    """
    absolute_url = request.build_absolute_uri()
    parsed = urlsplit(absolute_url)
    path_with_query = urlunsplit(("", "", parsed.path, parsed.query, ""))

    # Build host and scheme options from both direct request metadata and
    # reverse-proxy forwarding headers.
    host_candidates = [parsed.netloc]
    for header_name in ("HTTP_X_FORWARDED_HOST", "HTTP_HOST"):
        header_value = request.META.get(header_name, "")
        if header_value:
            first_host = header_value.split(",")[0].strip()
            if first_host:
                host_candidates.append(first_host)

    scheme_candidates = [parsed.scheme]
    forwarded_proto = request.META.get("HTTP_X_FORWARDED_PROTO", "")
    if forwarded_proto:
        for proto in forwarded_proto.split(","):
            normalized_proto = proto.strip().lower()
            if normalized_proto in {"http", "https"}:
                scheme_candidates.append(normalized_proto)

    if "http" not in scheme_candidates:
        scheme_candidates.append("http")
    if "https" not in scheme_candidates:
        scheme_candidates.append("https")

    candidates = [absolute_url]
    for scheme in scheme_candidates:
        for host in host_candidates:
            candidates.append(f"{scheme}://{host}{path_with_query}")

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(candidates))


@csrf_exempt
def twilio_sms_webhook(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    if not _is_valid_twilio_signature(request):
        return HttpResponseForbidden()

    required_fields = ["MessageSid", "From", "To"]
    if not all(field in request.POST for field in required_fields):
        return HttpResponse(status=400)

    payload = InboundSmsPayload(
        provider="twilio",
        provider_message_id=request.POST["MessageSid"],
        from_number=request.POST["From"],
        to_number=request.POST["To"],
        body=request.POST.get("Body", ""),
    )

    handle_inbound_sms(payload)
    return HttpResponse(status=200)


@login_required()
@staff_member_required
def inbound_messages(request):
    message_qs = InboundSmsMessage.objects.select_related("person")
    context = {
        "messages": message_qs,
        "unread_count": message_qs.filter(processed=False).count(),
    }
    return render(request, "prayer/inbound_messages.html", context)
