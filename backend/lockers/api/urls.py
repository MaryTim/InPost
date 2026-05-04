from django.urls import path
from .views import HealthView, RecommendView, LockerDetailView

urlpatterns = [
    path("health", HealthView.as_view(), name="health"),
    path("recommend", RecommendView.as_view(), name="recommend"),
    path("lockers/<str:code>", LockerDetailView.as_view(), name="locker-detail"),
]