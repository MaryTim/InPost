from django.contrib.gis.db import models as gis
from django.db import models


class Locker(models.Model):
    code = models.CharField(max_length=64, primary_key=True)
    address = models.CharField(max_length=512, blank=True)
    city = models.CharField(max_length=128, blank=True)
    point = gis.PointField(srid=4326)

    weekly_hours = models.JSONField(default=list, blank=True)
    weekly_hours_parsed = models.BooleanField(default=False)

    is_24_7 = models.BooleanField(default=False)
    accepts_returns = models.BooleanField(default=False)
    accepts_sends = models.BooleanField(default=False)
    easy_access = models.BooleanField(default=False)

    # "newfm", "next", "modular", "screenless"
    physical_type = models.CharField(max_length=32, blank=True)
    location_type = models.CharField(max_length=16, blank=True)

    # [{"code": "WAW124", "distance_m": 180}, ...]
    neighbors = models.JSONField(default=list, blank=True)

    last_seen_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} ({self.city})"
