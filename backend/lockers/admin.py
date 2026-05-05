from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import Locker


@admin.register(Locker)
class LockerAdmin(GISModelAdmin):
    list_display = ("code", "city", "location_type", "physical_type", "is_24_7", "easy_access")
    list_filter = ("is_24_7", "easy_access", "location_type", "physical_type")
    search_fields = ("code", "address", "city")
    readonly_fields = ("last_seen_at",)
