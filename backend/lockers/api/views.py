from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from lockers.models import Locker
from lockers.recommender.engine import recommend
from lockers.recommender.filters import FilterSet
from .serializers import RecommendRequestSerializer


class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok"})


class RecommendView(APIView):
    def post(self, request):
        ser = RecommendRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        f = d.get("filters") or {}
        open_at = f.get("open_at") or {}

        return Response(recommend(
            user_lat=d["user"]["lat"],
            user_lng=d["user"]["lng"],
            filters=FilterSet(
                require_24_7=f.get("require_24_7", False),
                require_easy_access=f.get("require_easy_access", False),
                open_at_day=open_at.get("day"),
                open_at_time=open_at.get("time"),
            ),
            radius_m=d.get("radius_m", 500),
            limit=d.get("limit", 5),
        ))


class LockerDetailView(APIView):
    def get(self, request, code: str):
        l = get_object_or_404(Locker, code=code)
        return Response({
            "code": l.code,
            "address": l.address,
            "city": l.city,
            "lat": l.point.y,
            "lng": l.point.x,
            "is_24_7": l.is_24_7,
            "location_type": l.location_type,
            "physical_type": l.physical_type,
            "easy_access": l.easy_access,
            "weekly_hours": l.weekly_hours,
            "neighbors": l.neighbors,
        })
