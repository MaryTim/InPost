import logging
from .hours import parse_hours

logger = logging.getLogger(__name__)

def parse_locker(raw: dict) -> dict | None:
    try:
        if raw.get("country") != "PL":
            return None
        if raw.get("status") != "Operating":
            return None

        types = raw.get("type") or []
        if "parcel_locker" not in types:
            return None
        loc = raw.get("location") or {}
        lat, lng = loc.get("latitude"), loc.get("longitude")
        if lat is None or lng is None:
            return None

        functions = set(raw.get("functions") or [])
        accepts_sends = any(f.endswith("_send") for f in functions)
        accepts_returns = any(f.endswith("_reverse_return_send") for f in functions)

        weekly, parsed_ok = parse_hours(raw.get("operating_hours_extended"))

        addr = raw.get("address") or {}
        addr_details = raw.get("address_details") or {}

        return {
            "code": raw["name"],
            "address": addr.get("line1", ""),
            "city": addr_details.get("city", ""),
            "lat": lat,
            "lng": lng,
            "weekly_hours": weekly,
            "weekly_hours_parsed": parsed_ok,
            "is_24_7": bool(raw.get("location_247", False)),
            "accepts_returns": accepts_returns,
            "accepts_sends": accepts_sends,
            "location_type": raw.get("location_type", "") or "",
            "physical_type": raw.get("physical_type", "") or "",
            "easy_access": bool(raw.get("easy_access_zone", False)),
        }
    except Exception as e:
        logger.warning("Failed to parse record %s: %s", raw.get("name"), e)
        return None
