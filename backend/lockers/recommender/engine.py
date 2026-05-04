from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Max

from lockers.models import Locker
from .filters import FilterSet, matches
from .score import score_candidate, R_ANCHOR_M
from .warnings import build_warnings


def recommend(user_lat: float, user_lng: float, filters: FilterSet, radius_m: int = R_ANCHOR_M, limit: int = 5) -> dict:
    user = Point(user_lng, user_lat, srid=4326)

    candidates = list(
        Locker.objects
        .filter(point__distance_lte=(user, D(m=radius_m)))
        .annotate(d=Distance("point", user))
        .order_by("d")
    )

    neighbor_codes = {n["code"] for c in candidates for n in c.neighbors}
    neighbor_lockers = {
        l.code: l for l in Locker.objects.filter(code__in=neighbor_codes)
    }

    results = []
    for c in candidates:
        if not matches(c, filters):
            continue

        per_neighbor = []
        n_total = len(c.neighbors)
        n_matching = 0
        for n in c.neighbors:
            nl = neighbor_lockers.get(n["code"])
            ok = bool(nl and matches(nl, filters))
            if ok:
                n_matching += 1
            per_neighbor.append({
                "code": n["code"],
                "lat": nl.point.y if nl else None,
                "lng": nl.point.x if nl else None,
                "distance_m": n["distance_m"],
                "matches_all_filters": ok,
            })

        breakdown = score_candidate(c.d.m, n_total, n_matching)
        warnings = build_warnings(c, n_total, n_matching)

        results.append({
            "code": c.code,
            "address": c.address,
            "city": c.city,
            "lat": c.point.y,
            "lng": c.point.x,
            "distance_m": int(c.d.m),
            "is_24_7": c.is_24_7,
            "location_type": c.location_type,
            "easy_access": c.easy_access,
            "score": round(breakdown.total, 3),
            "score_breakdown": {
                "proximity": round(breakdown.proximity, 3),
                "fallback_robustness": round(breakdown.fallback_robustness, 3),
            },
            "fallbacks": per_neighbor,
            "warnings": warnings,
        })

    results.sort(key=lambda r: r["score"], reverse=True)

    last = Locker.objects.aggregate(Max("last_seen_at"))["last_seen_at__max"]
    return {
        "results": results[:limit],
        "meta": {"dataset_refreshed_at": last.isoformat() if last else None},
    }
