from django.shortcuts import render, redirect
from prayer.forms import NewGroupForm, NewPersonForm
from prayer.models import Person, PrayerGroup
from django.contrib import messages


# from django.contrib.messages import get_messages

# Create your views here.
def index(request) -> render:
    """
    Home page for prayer app.
    """
    context = {}
    return render(request, "prayer/index.html", context)


def new_message(request) -> render:
    """
    Create a new message.
    """
    context = {}
    return render(request, "prayer/new_message.html", context)


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


def group(request, group_id):
    """
    Group detail page, user editable.
    """
    group_ = PrayerGroup.objects.get(id=group_id)
    context = {
        "group": group_,
        "form": NewGroupForm(PrayerGroup.objects.get(id=group_id).__dict__),
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


def delete_group(request, group_id):
    """
    Delete the group with id of group_id.
    """
    group_ = PrayerGroup.objects.get(id=group_id)
    group_.delete()
    messages.success(request, f"You've successfully deleted the {group_.name} group.")
    return redirect("prayer:groups")


def prayer_requests(request) -> render:
    """
    List of prayer requests.
    """
    context = {}
    return render(request, "prayer/prayer_request.html", context)


def people(request) -> render:
    """
    List of people.
    """
    context = {
        "new_person_form": NewPersonForm(),
        "people_list": Person.objects.all(),
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
