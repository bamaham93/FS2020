from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Hymnal(models.Model):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    publisher = models.CharField(max_length=255, blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    denomination = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=100, blank=True)
    source_url = models.URLField(blank=True)

    class Meta:
        ordering = ["title", "publication_year"]

    def __str__(self):
        return f"{self.title} ({self.code})"


class Topic(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ScriptureReference(models.Model):
    reference = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ["reference"]

    def __str__(self):
        return self.reference


class Tune(models.Model):
    name = models.CharField(max_length=255)
    meter = models.CharField(max_length=100, blank=True)
    key = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=255, blank=True)
    composer = models.CharField(max_length=255, blank=True)
    source_url = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "meter"],
                name="unique_tune_name_meter",
            )
        ]

    def __str__(self):
        return self.name


class Hymn(models.Model):
    canonical_title = models.CharField(max_length=255)
    normalized_title = models.CharField(max_length=255, db_index=True)
    first_line = models.CharField(max_length=500, blank=True)
    author = models.CharField(max_length=255, blank=True)
    meter = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, blank=True)
    copyright_status = models.CharField(max_length=255, blank=True)
    source_url = models.URLField(blank=True)
    topics = models.ManyToManyField(Topic, blank=True)
    scripture_references = models.ManyToManyField(ScriptureReference, blank=True)

    class Meta:
        ordering = ["canonical_title"]
        constraints = [
            models.UniqueConstraint(
                fields=["normalized_title", "first_line", "author"],
                name="unique_hymn_identity",
            )
        ]

    def __str__(self):
        return self.canonical_title


class HymnImportBatch(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    source = models.CharField(max_length=50, default="hymnary")
    hymnal_code = models.CharField(max_length=50)
    source_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.source} {self.hymnal_code} import {self.pk}"

    def approve(self):
        self.status = self.STATUS_APPROVED
        self.approved_at = timezone.now()
        self.save(update_fields=["status", "approved_at"])
        self.entries.update(is_approved=True)

    def reject(self):
        self.status = self.STATUS_REJECTED
        self.save(update_fields=["status"])


class HymnalEntry(models.Model):
    hymnal = models.ForeignKey(Hymnal, on_delete=models.CASCADE, related_name="entries")
    number = models.CharField(max_length=20)
    title_as_printed = models.CharField(max_length=255)
    first_line_as_printed = models.CharField(max_length=500, blank=True)
    tune_as_printed = models.CharField(max_length=255, blank=True)
    meter_as_printed = models.CharField(max_length=100, blank=True)
    key = models.CharField(max_length=100, blank=True)
    publication_date = models.CharField(max_length=50, blank=True)
    source_url = models.URLField(blank=True)
    hymn = models.ForeignKey(Hymn, null=True, blank=True, on_delete=models.SET_NULL, related_name="entries")
    tune = models.ForeignKey(Tune, null=True, blank=True, on_delete=models.SET_NULL, related_name="entries")
    topics = models.ManyToManyField(Topic, blank=True)
    scripture_references = models.ManyToManyField(ScriptureReference, blank=True)
    import_batch = models.ForeignKey(HymnImportBatch, null=True, blank=True, on_delete=models.SET_NULL, related_name="entries")
    is_approved = models.BooleanField(default=False)
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["hymnal__title", "number"]
        constraints = [
            models.UniqueConstraint(
                fields=["hymnal", "number"],
                name="unique_hymnal_number",
            )
        ]

    def __str__(self):
        return f"{self.hymnal.code} #{self.number} {self.title_as_printed}"


class HymnImportIssue(models.Model):
    batch = models.ForeignKey(HymnImportBatch, on_delete=models.CASCADE, related_name="issues")
    source_url = models.URLField(blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.message


class ServicePlan(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_FINALIZED = "finalized"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_FINALIZED, "Finalized"),
    ]

    title = models.CharField(max_length=255)
    service_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    finalized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-service_date", "-created_at"]

    def __str__(self):
        return self.title

    def finalize(self):
        self.status = self.STATUS_FINALIZED
        self.finalized_at = timezone.now()
        self.save(update_fields=["status", "finalized_at"])
        for item in self.items.select_related("hymnal_entry"):
            HymnUsage.objects.get_or_create(
                service_plan=self,
                hymnal_entry=item.hymnal_entry,
                defaults={"used_on": self.service_date or timezone.localdate()},
            )


class ServicePlanItem(models.Model):
    service_plan = models.ForeignKey(ServicePlan, on_delete=models.CASCADE, related_name="items")
    hymnal_entry = models.ForeignKey(HymnalEntry, on_delete=models.CASCADE, related_name="plan_items")
    position = models.PositiveIntegerField(default=1)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"{self.service_plan}: {self.hymnal_entry}"


class HymnUsage(models.Model):
    hymnal_entry = models.ForeignKey(HymnalEntry, on_delete=models.CASCADE, related_name="usages")
    service_plan = models.ForeignKey(ServicePlan, on_delete=models.CASCADE, related_name="usage_records")
    used_on = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-used_on", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["hymnal_entry", "service_plan"],
                name="unique_usage_per_plan",
            )
        ]

    def __str__(self):
        return f"{self.hymnal_entry} used {self.used_on}"
