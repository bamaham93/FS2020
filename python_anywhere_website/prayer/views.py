from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from prayer.forms import NewGroupForm, NewPersonForm, NewMessageForm, PermissionsForm
from prayer.models import Person, PrayerGroup

try:
    import logic.queries
    from logic.Messaging.sms import SMSMessage
    from logic.queries import PrayerGroupQueries, PrayerMessageQueries
except ModuleNotFoundError:
    pass

# from django.contrib.messages import get_messages

# Create your views here.
def index(request) -> render:
    """
    Home page for prayer app.
    """
    context = {}
    return render(request, "prayer/index.html", context)


@login_required()
def new_message(request) -> render:
    """
    Create a new message.
    """
    # Check if logic.queries classes are available
    if 'PrayerMessageQueries' in globals() and 'PrayerGroupQueries' in globals():
        try:
            msg_query = PrayerMessageQueries()
            pg_queries = PrayerGroupQueries()
            prayer_groups = pg_queries.get_all()
            all_messages = reversed(msg_query.get_all_messages())
        except (AttributeError, ImportError):
            # Fallback if queries fail
            from prayer.models import PrayerMessage
            prayer_groups = PrayerGroup.objects.all()
            all_messages = reversed(PrayerMessage.objects.all())
    else:
        # Fallback when logic.queries is not available
        from prayer.models import PrayerMessage
        prayer_groups = PrayerGroup.objects.all()
        all_messages = reversed(PrayerMessage.objects.all())

    context = {
        "form": NewMessageForm(),
        "messages": all_messages,
        "prayer_groups": prayer_groups,
    }
    if request.method == "POST":
        form = NewMessageForm(request.POST)
        form.save()
        messages.success(request, "Your message was saved!")
        redirect("prayer:new_message")
    return render(request, "prayer/new_message.html", context)


def message_detail(request, id):
    """
    See message details, send to prayer groups.
    Todo: Move code pertaining to sending sms messages to the function below.
    """
    # Check if logic.queries classes are available
    if 'PrayerMessageQueries' in globals() and 'PrayerGroupQueries' in globals():
        try:
            pm_queries = PrayerMessageQueries()
            message = pm_queries.get_message_by_id(id=id)
            pg_queries = PrayerGroupQueries()
            prayer_groups = pg_queries.get_all()
        except (AttributeError, ImportError):
            # Fallback if queries fail
            from prayer.models import PrayerMessage
            message = PrayerMessage.objects.get(id=id)
            prayer_groups = PrayerGroup.objects.all()
            pg_queries = None
    else:
        # Fallback when logic.queries is not available
        from prayer.models import PrayerMessage
        message = PrayerMessage.objects.get(id=id)
        prayer_groups = PrayerGroup.objects.all()
        pg_queries = None

    context = {
        "message": message,
        "prayer_groups": prayer_groups,
    }

    # Send messages
    if request.method == "POST":
        checks = request.POST.getlist("groups")

        people_set = set()
        # print(people_set)

        for group in checks:  # group is a string the name of the group.
            if pg_queries is not None:
                try:
                    group_ = pg_queries.get_group_members(
                        group
                    )  # group_ is a queryset of person objects.
                except (AttributeError, ImportError):
                    group_ = PrayerGroup.objects.get(name=group).people.all()
            else:
                group_ = PrayerGroup.objects.get(name=group).people.all()
            people_set.update(group_)

        # Filter to only people who have consented to SMS - use database filtering
        consented_people = set(
            Person.objects.filter(
                id__in=[p.id for p in people_set],
                sms_consent=True,
                phone_number__isnull=False
            ).exclude(phone_number='')
        )
        
        if consented_people:
            # Check if SMSMessage is available
            if 'SMSMessage' in globals():
                try:
                    sms_message = SMSMessage(
                        body=message.message, contacts=consented_people, testing=False
                    )
                    sms_message.send()
                    messages.success(request, f"Message sent to {len(consented_people)} recipient(s) who have consented to SMS.")
                except (AttributeError, ImportError) as e:
                    messages.error(request, f"Failed to send SMS messages: {e}")
            else:
                messages.warning(request, "SMS functionality is not available.")
        else:
            messages.warning(request, "No recipients with SMS consent found in the selected groups.")

        # for person in people_set:  # Used a set so to eliminate duplicate messages.
        #     print(f"First Name: {person.first_name}")
        #     print(f"Last Name: {person.last_name}")
        #     print(f"Ph: {person.phone_number}")
        #     print("\n")
    return render(request, "prayer/message_detail.html", context)


@login_required()
def send_message(request, id: int):
    """
    Todo: Move code related to sending text messages into this function
    instead of handling it in the views.
    """
    # Check if classes are available
    if 'PrayerMessageQueries' in globals() and 'SMSMessage' in globals():
        try:
            message = PrayerMessageQueries.get_message_by_id(id=id)
            body = message.message
            # SMSMessage.contacts list of tuples
            sms = SMSMessage(body=body)
            sms.send()
        except (AttributeError, ImportError) as e:
            messages.error(request, f"Failed to send message: {e}")
            return redirect("prayer:new_message")
    else:
        messages.error(request, "SMS functionality is not available.")
    return redirect("prayer:new_message")


@login_required()
def groups(request) -> render:
    """
    List of groups.
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
    if 'PrayerGroupQueries' in globals():
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
    context = {}
    return render(request, "prayer/prayer_request.html", context)


@login_required()
def people(request) -> render:
    """
    List of people.
    """
    context = {
        "new_person_form": NewPersonForm(),
        "people_list": Person.objects.all(),  # TODO Move to logic/queries.py
        # 'messages': get_messages(request)
    }
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
