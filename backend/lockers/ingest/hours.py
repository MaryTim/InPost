DAY_MAP = {
    "monday": "mon", "tuesday": "tue", "wednesday": "wed", "thursday": "thu",
    "friday": "fri", "saturday": "sat", "sunday": "sun",
}


def parse_hours(extended: dict | None) -> tuple[list, bool]:
    if not extended:
        return [], False
    customer = extended.get("customer")
    if not customer:
        return [], False

    out = []
    for api_day, windows in customer.items():
        day = DAY_MAP.get(api_day)
        if not day or not windows:
            continue
        for w in windows:
            try:
                out.append({
                    "day": day,
                    "start": _minutes_to_time(w["start"]),
                    "end": _minutes_to_time(w["end"]),
                })
            except (KeyError, TypeError, ValueError):
                continue

    return out, bool(out)


def _minutes_to_time(m: int) -> str:
    h, mm = divmod(int(m), 60)
    if h >= 24:
        h, mm = 23, 59
    return f"{h:02d}:{mm:02d}"