from django.shortcuts import render, redirect
from prayer.forms import NewGroupForm, NewPersonForm, NewMessageForm, PermissionsForm
from prayer.models import Person, PrayerGroup, PrayerMessage

import logic.queries
from logic.queries import PersonQueries, PrayerGroupQueries,  PrayerMessageQueries
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from prayer.Messaging.sms import SMSMessage


# from django.contrib.messages import get_messages

# Create your views here.
def index(request) -> render:
    """
    Home page for prayer app.
    """
    group_members = PrayerGroupQueries()
    context = {
        'group_members': group_members.get_group_members(group='CBC Members'),
    }
    return render(request, "prayer/index.html", context)


@login_required
def new_message(request) -> render:
    """
    Create a new message.
    """
    msg_query = PrayerMessageQueries()
    context = {
        'form': NewMessageForm(),
        'messages': reversed(msg_query.get_all_messages())
    }
    if request.method == "POST":
        form = NewMessageForm(request.POST)
        form.save()
        messages.success(request, "Your message was saved!")
    return render(request, "prayer/new_message.html", context)


def message_detail(request, id):
    """
    See message details, send to prayer groups.
    """

    pm_queries = logic.queries.PrayerMessageQueries()
    message = pm_queries.get_message_by_id(id=id)
    pg_queries = logic.queries.PrayerGroupQueries()

    prayer_groups = pg_queries.get_all()
    context = {
        'message': message,
        'prayer_groups': prayer_groups,
    }

    if request.method == 'POST':
        checks = request.POST.getlist('groups')
        print(checks)
    return render(request, 'prayer/message_detail.html', context)


def send_message(request, id):
    """
    """
    message = PrayerMessageQueries.get_message_by_id(id=id)
    body = message.message

    # SMSMessage.contacts list of tuples
    sms = SMSMessage(body=body)
    sms.send()
    return redirect()


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
    membership = PrayerGroupQueries()
    context = {
        "group": group_,
        "form": NewGroupForm(PrayerGroup.objects.get(id=group_id).__dict__),
        "group_membership": membership.get_group_members(group=group_.name),
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
            form.save()
            messages.success(request, "Your submission was saved!")
        else:
            context["new_person_form"] = NewPersonForm(request.POST)
            messages.warning(request, "There was a problem saving your form.")
    return render(request, "prayer/prayer-people.html", context)


def delete_person(request, person_id: int) -> redirect:
    """ """
    person = Person.objects.get(id=person_id)
    person.delete()
    messages.success(
        request, f"You have successfully deleted {person.first_name} {person.last_name}"
    )
    return redirect("prayer:people")


def permissions(request, id):
    context = {'form': PermissionsForm()}
    return render(request, 'prayer/permissions.html', context)
