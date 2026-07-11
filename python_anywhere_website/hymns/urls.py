from django.urls import path

from hymns import views

app_name = "hymns"

urlpatterns = [
    path("", views.index, name="index"),
    path("hymnals/<str:code>/", views.hymnal_detail, name="hymnal_detail"),
    path("imports/", views.import_batches, name="import_batches"),
    path("imports/<int:batch_id>/", views.import_batch_detail, name="import_batch_detail"),
    path("imports/<int:batch_id>/approve/", views.approve_import_batch, name="approve_import_batch"),
    path("imports/<int:batch_id>/reject/", views.reject_import_batch, name="reject_import_batch"),
    path("plans/", views.service_plan_list, name="service_plan_list"),
    path("plans/new/", views.service_plan_create, name="service_plan_create"),
    path("plans/<int:plan_id>/", views.service_plan_detail, name="service_plan_detail"),
    path("plans/<int:plan_id>/add/", views.add_plan_item, name="add_plan_item"),
    path("plans/<int:plan_id>/suggestions/<int:entry_id>/add/", views.add_suggested_item, name="add_suggested_item"),
    path("plans/<int:plan_id>/items/<int:item_id>/remove/", views.remove_plan_item, name="remove_plan_item"),
    path("plans/<int:plan_id>/finalize/", views.finalize_plan, name="finalize_plan"),
    path("plans/<int:plan_id>/print/", views.printable_plan, name="printable_plan"),
]

