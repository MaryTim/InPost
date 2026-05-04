from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from lockers.ingest.client import iter_polish_points
from lockers.ingest.parser import parse_locker
from lockers.models import Locker


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        count = 0
        for raw in iter_polish_points():
            parsed = parse_locker(raw)
            if not parsed:
                continue

            lat = parsed.pop("lat")
            lng = parsed.pop("lng")
            parsed["point"] = Point(lng, lat, srid=4326)

            Locker.objects.update_or_create(code=parsed["code"], defaults=parsed)
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Done. {count} lockers."))