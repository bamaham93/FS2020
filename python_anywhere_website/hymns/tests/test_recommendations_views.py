from datetime import timedelta

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import Client, TestCase
from django.utils import timezone
from unittest.mock import patch

from hymns.models import Hymnal, HymnalEntry, HymnUsage, ServicePlan, ServicePlanItem
from hymns import views
from hymns.services import recommend_entries


class RecommendationAndViewTests(TestCase):
    def setUp(self):
        self.hymnal = Hymnal.objects.create(code="UMH", title="The United Methodist Hymnal")
        self.old_entry = HymnalEntry.objects.create(
            hymnal=self.hymnal,
            number="1",
            title_as_printed="Older Use",
            tune_as_printed="OLD",
            is_approved=True,
        )
        self.recent_entry = HymnalEntry.objects.create(
            hymnal=self.hymnal,
            number="2",
            title_as_printed="Recent Use",
            tune_as_printed="RECENT",
            is_approved=True,
        )
        old_plan = ServicePlan.objects.create(title="Old", service_date=timezone.localdate() - timedelta(days=300))
        recent_plan = ServicePlan.objects.create(title="Recent", service_date=timezone.localdate())
        HymnUsage.objects.create(hymnal_entry=self.old_entry, service_plan=old_plan, used_on=old_plan.service_date)
        HymnUsage.objects.create(hymnal_entry=self.recent_entry, service_plan=recent_plan, used_on=recent_plan.service_date)

    def test_recent_usage_is_penalized(self):
        recommendations = recommend_entries(limit=2)
        self.assertEqual(recommendations[0], self.old_entry)

    def test_staff_can_finalize_plan_and_record_usage(self):
        user = User.objects.create_user(username="staff", password="pw", is_staff=True)
        client = Client()
        client.force_login(user)
        plan = ServicePlan.objects.create(title="Sunday", service_date=timezone.localdate(), created_by=user)
        ServicePlanItem.objects.create(service_plan=plan, hymnal_entry=self.old_entry, position=1)

        response = client.post(f"/hymns/plans/{plan.id}/finalize/")
        self.assertEqual(response.status_code, 302)
        plan.refresh_from_db()
        self.assertEqual(plan.status, ServicePlan.STATUS_FINALIZED)
        self.assertTrue(HymnUsage.objects.filter(service_plan=plan, hymnal_entry=self.old_entry).exists())

    def test_index_and_printable_views_load(self):
        user = User.objects.create_user(username="staff2", password="pw", is_staff=True)
        plan = ServicePlan.objects.create(title="Sunday", service_date=timezone.localdate(), created_by=user)
        ServicePlanItem.objects.create(service_plan=plan, hymnal_entry=self.old_entry, position=1)

        class Request:
            pass

        request = Request()
        request.user = user

        captured = []

        def fake_render(_request, template, context):
            captured.append((template, context))
            return HttpResponse("ok")

        with patch.object(views, "render", fake_render):
            self.assertEqual(views.index(request).status_code, 200)
            self.assertEqual(views.printable_plan(request, plan.id).status_code, 200)

        self.assertEqual(captured[0][0], "hymns/index.html")
        self.assertEqual(captured[1][0], "hymns/printable_plan.html")
        self.assertEqual(list(captured[1][1]["items"])[0].hymnal_entry, self.old_entry)
