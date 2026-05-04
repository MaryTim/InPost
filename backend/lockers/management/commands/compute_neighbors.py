import time
from django.core.management.base import BaseCommand
from django.db import connection

R_FALLBACK_M = 300
# ~500m bbox in degrees at Poland's latitude
BBOX_DEGREES = 0.005


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        start = time.time()

        with connection.cursor() as cursor:
            self.stdout.write("Computing neighbors (bbox + accurate distance)...")
            cursor.execute("""
                UPDATE lockers_locker AS target
                SET neighbors = COALESCE(sub.neighbor_data, '[]'::jsonb)
                FROM (
                    SELECT l1.code,
                           jsonb_agg(
                               jsonb_build_object(
                                   'code', l2.code,
                                   'distance_m', ROUND(ST_Distance(l1.point::geography, l2.point::geography))::int
                               )
                               ORDER BY ST_Distance(l1.point::geography, l2.point::geography)
                           ) AS neighbor_data
                    FROM lockers_locker l1
                    JOIN lockers_locker l2
                      ON l1.code <> l2.code
                     AND l1.point && ST_Expand(l2.point, %s)
                     AND ST_Distance(l1.point::geography, l2.point::geography) <= %s
                    GROUP BY l1.code
                ) AS sub
                WHERE target.code = sub.code
            """, [BBOX_DEGREES, R_FALLBACK_M])

            cursor.execute("""
                UPDATE lockers_locker
                SET neighbors = '[]'::jsonb
                WHERE neighbors IS NULL OR jsonb_typeof(neighbors) <> 'array'
            """)

        elapsed = time.time() - start
        self.stdout.write(self.style.SUCCESS(f"Done in {elapsed:.1f}s"))