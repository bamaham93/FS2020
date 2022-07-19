from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Registered tag for Jinja Templates to check if user is a member of a group.
    """
    return user.groups.filter(name=group_name).exists()

def is_group(user, group):
    if user.groups.filter(name=group):
        return True
    else:
        return False

def is_groups(*args):
    """
    """
