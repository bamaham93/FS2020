from django.shortcuts import render, redirect
from prayer.forms import NewGroupForm, NewPersonForm
from prayer.models import Person
from django.contrib import messages
# from django.contrib.messages import get_messages

# Create your views here.
def index(request) -> render:
    """
    """
    context = {}
    return render(request, 'prayer/index.html', context)


def new_message(request) -> render:
    """
    """
    context = {}
    return render(request, 'prayer/new_message.html', context)


def groups(request) -> render:
    """
    """
    context = {'new_group_form': NewGroupForm()}
    return render(request, 'prayer/groups.html', context)

def prayer_requests(request) -> render:
    """

    """
    context = {}
    return render(request, 'prayer/prayer_request.html', context)


def people(request) -> render:
    """
    """
    context = {
        'new_person_form': NewPersonForm(),
        'people_list': Person.objects.all(),
        # 'messages': get_messages(request)
    }
    if request.method == "POST":
        form = NewPersonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your submission was saved!')
        else:
            context['new_person_form'] = NewPersonForm(request.POST)
            messages.warning(request, 'There was a problem saving your form.')
    return render(request, 'prayer/prayer-people.html', context)


def delete_person(request, person_id:int) -> redirect:
    """
    """
    person = Person.objects.get(id=person_id)
    person.delete()
    messages.success(request, f'You have successfully deleted {person.first_name} {person.last_name}')
    return redirect('prayer:people')
