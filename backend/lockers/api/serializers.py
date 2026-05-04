from rest_framework import serializers

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


class UserLocationSerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lng = serializers.FloatField(min_value=-180, max_value=180)


class OpenAtSerializer(serializers.Serializer):
    day = serializers.ChoiceField(choices=DAYS)
    time = serializers.RegexField(regex=r"^\d{2}:\d{2}$")


class FilterSerializer(serializers.Serializer):
    require_24_7 = serializers.BooleanField(required=False, default=False)
    require_easy_access = serializers.BooleanField(required=False, default=False)
    open_at = OpenAtSerializer(required=False)


class RecommendRequestSerializer(serializers.Serializer):
    user = UserLocationSerializer()
    filters = FilterSerializer(required=False)
    radius_m = serializers.IntegerField(min_value=50, max_value=5000, default=500, required=False)
    limit = serializers.IntegerField(min_value=1, max_value=20, default=5, required=False)
