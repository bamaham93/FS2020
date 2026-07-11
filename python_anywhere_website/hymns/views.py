from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from hymns.forms import ServicePlanForm, ServicePlanItemForm
from hymns.models import Hymnal, HymnalEntry, HymnImportBatch, ServicePlan, ServicePlanItem
from hymns.services import recommend_entries


def index(request):
    context = {
        "hymnals": Hymnal.objects.annotate(entry_count=Count("entries")),
        "plans": ServicePlan.objects.all()[:8],
        "pending_batches": HymnImportBatch.objects.filter(
            status=HymnImportBatch.STATUS_PENDING
        )[:5],
    }
    return render(request, "hymns/index.html", context)


def hymnal_detail(request, code):
    hymnal = get_object_or_404(Hymnal, code=code)
    entries = hymnal.entries.filter(is_approved=True).select_related("tune")
    return render(request, "hymns/hymnal_detail.html", {"hymnal": hymnal, "entries": entries})


@login_required
@staff_member_required
def import_batches(request):
    batches = HymnImportBatch.objects.prefetch_related("entries", "issues")
    return render(request, "hymns/import_batches.html", {"batches": batches})


@login_required
@staff_member_required
def import_batch_detail(request, batch_id):
    batch = get_object_or_404(HymnImportBatch, id=batch_id)
    entries = batch.entries.select_related("hymnal", "tune").prefetch_related("topics")
    issues = batch.issues.all()
    return render(
        request,
        "hymns/import_batch_detail.html",
        {"batch": batch, "entries": entries, "issues": issues},
    )


@login_required
@staff_member_required
def approve_import_batch(request, batch_id):
    if request.method != "POST":
        return redirect("hymns:import_batch_detail", batch_id=batch_id)
    batch = get_object_or_404(HymnImportBatch, id=batch_id)
    batch.approve()
    messages.success(request, "Import batch approved for recommendations.")
    return redirect("hymns:import_batch_detail", batch_id=batch.id)


@login_required
@staff_member_required
def reject_import_batch(request, batch_id):
    if request.method != "POST":
        return redirect("hymns:import_batch_detail", batch_id=batch_id)
    batch = get_object_or_404(HymnImportBatch, id=batch_id)
    batch.reject()
    messages.warning(request, "Import batch rejected.")
    return redirect("hymns:import_batch_detail", batch_id=batch.id)


@login_required
@staff_member_required
def service_plan_list(request):
    plans = ServicePlan.objects.all()
    return render(request, "hymns/service_plan_list.html", {"plans": plans})


@login_required
@staff_member_required
def service_plan_create(request):
    form = ServicePlanForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        plan = form.save(commit=False)
        plan.created_by = request.user
        plan.save()
        messages.success(request, "Service plan created.")
        return redirect("hymns:service_plan_detail", plan_id=plan.id)
    return render(request, "hymns/service_plan_form.html", {"form": form})


@login_required
@staff_member_required
def service_plan_detail(request, plan_id):
    plan = get_object_or_404(ServicePlan, id=plan_id)
    items = plan.items.select_related("hymnal_entry", "hymnal_entry__hymnal")
    item_form = ServicePlanItemForm()
    suggestions = recommend_entries(limit=6)
    return render(
        request,
        "hymns/service_plan_detail.html",
        {
            "plan": plan,
            "items": items,
            "item_form": item_form,
            "suggestions": suggestions,
        },
    )


@login_required
@staff_member_required
def add_plan_item(request, plan_id):
    plan = get_object_or_404(ServicePlan, id=plan_id)
    if request.method != "POST":
        return redirect("hymns:service_plan_detail", plan_id=plan.id)
    form = ServicePlanItemForm(request.POST)
    if form.is_valid():
        item = form.save(commit=False)
        item.service_plan = plan
        if not item.position:
            item.position = plan.items.count() + 1
        item.save()
        messages.success(request, "Hymn added to plan.")
    else:
        messages.warning(request, "Could not add that hymn to the plan.")
    return redirect("hymns:service_plan_detail", plan_id=plan.id)


@login_required
@staff_member_required
def add_suggested_item(request, plan_id, entry_id):
    if request.method != "POST":
        return redirect("hymns:service_plan_detail", plan_id=plan_id)
    plan = get_object_or_404(ServicePlan, id=plan_id)
    entry = get_object_or_404(HymnalEntry, id=entry_id, is_approved=True)
    ServicePlanItem.objects.create(
        service_plan=plan,
        hymnal_entry=entry,
        position=plan.items.count() + 1,
    )
    messages.success(request, f"Added {entry.title_as_printed}.")
    return redirect("hymns:service_plan_detail", plan_id=plan.id)


@login_required
@staff_member_required
def remove_plan_item(request, plan_id, item_id):
    if request.method != "POST":
        return redirect("hymns:service_plan_detail", plan_id=plan_id)
    item = get_object_or_404(ServicePlanItem, id=item_id, service_plan_id=plan_id)
    item.delete()
    messages.success(request, "Hymn removed from plan.")
    return redirect("hymns:service_plan_detail", plan_id=plan_id)


@login_required
@staff_member_required
def finalize_plan(request, plan_id):
    if request.method != "POST":
        return redirect("hymns:service_plan_detail", plan_id=plan_id)
    plan = get_object_or_404(ServicePlan, id=plan_id)
    plan.finalize()
    messages.success(request, "Service plan finalized and usage history recorded.")
    return redirect("hymns:service_plan_detail", plan_id=plan.id)


@login_required
@staff_member_required
def printable_plan(request, plan_id):
    plan = get_object_or_404(ServicePlan, id=plan_id)
    items = plan.items.select_related("hymnal_entry", "hymnal_entry__hymnal")
    return render(request, "hymns/printable_plan.html", {"plan": plan, "items": items})
