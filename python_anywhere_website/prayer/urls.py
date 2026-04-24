from django.urls import path

from . import views

app_name = "prayer"

urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index"),
    path("signup", views.public_signup, name="public_signup"),
    path("new-message", views.new_message, name="new_message"),
    path("message-detail/<int:id>", views.message_detail, name="message-detail"),
    path("send-message/<int:id>", views.send_message, name="send_message"),
    path("groups", views.groups, name="groups"),
    path("group/detail/<int:group_id>", views.group, name="group"),
    path("groups/delete/<int:group_id>", views.delete_group, name="delete_group"),
    path("prayer-requests", views.prayer_requests, name="prayer_requests"),
    path(
        "prayer-requests/delete/<int:id>",
        views.delete_prayer_request,
        name="delete_prayer_request",
    ),
    path(
        "prayer-requests/mark-important/<int:id>",
        views.toggle_important,
        name="toggle_important",
    ),
    path(
        "prayer-requests/mark-complete/<int:id>",
        views.toggle_complete,
        name="toggle_complete",
    ),
    path(
        "prayer-requests/answer/<int:id>",
        views.answer_prayer_request,
        name="answer_prayer_request",
    ),
    path("people", views.people, name="people"),
    path("delete-person/<person_id>", views.delete_person, name="delete_person"),
    path("permissions/<int:id>", views.permissions, name="permissions"),
    path("messages/inbound", views.inbound_messages, name="inbound_messages"),
]

