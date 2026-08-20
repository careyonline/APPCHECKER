from django.contrib import admin

from .models import AppCheckRecord


@admin.register(AppCheckRecord)
class AppCheckRecordAdmin(admin.ModelAdmin):
    list_display = ("app_name", "dev_name", "prediction", "confidence", "risk_level", "created_at")
    list_filter = ("prediction", "risk_level", "app_age")
    search_fields = ("app_name", "dev_name")
    ordering = ("-created_at",)
