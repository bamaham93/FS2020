from django.contrib import admin

from hymns.models import (
    Hymn,
    Hymnal,
    HymnalEntry,
    HymnImportBatch,
    HymnImportIssue,
    HymnUsage,
    ScriptureReference,
    ServicePlan,
    ServicePlanItem,
    Topic,
    Tune,
)


@admin.register(HymnalEntry)
class HymnalEntryAdmin(admin.ModelAdmin):
    list_display = ("hymnal", "number", "title_as_printed", "tune_as_printed", "is_approved")
    list_filter = ("hymnal", "is_approved")
    search_fields = ("title_as_printed", "first_line_as_printed", "tune_as_printed", "number")


class ServicePlanItemInline(admin.TabularInline):
    model = ServicePlanItem
    extra = 0


@admin.register(ServicePlan)
class ServicePlanAdmin(admin.ModelAdmin):
    list_display = ("title", "service_date", "status", "created_at")
    list_filter = ("status",)
    inlines = [ServicePlanItemInline]


admin.site.register(Hymnal)
admin.site.register(Hymn)
admin.site.register(Tune)
admin.site.register(Topic)
admin.site.register(ScriptureReference)
admin.site.register(HymnImportBatch)
admin.site.register(HymnImportIssue)
admin.site.register(HymnUsage)
