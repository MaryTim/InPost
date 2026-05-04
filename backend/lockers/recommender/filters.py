from dataclasses import dataclass


@dataclass
class FilterSet:
    require_24_7: bool = False
    require_easy_access: bool = False
    open_at_day: str | None = None
    open_at_time: str | None = None


def matches(locker, f: FilterSet) -> bool:
    if f.require_24_7 and not locker.is_24_7:
        return False
    if f.require_easy_access and not locker.easy_access:
        return False
    if f.open_at_day and f.open_at_time:
        if not _is_open_at(locker, f.open_at_day, f.open_at_time):
            return False
    return True


def _is_open_at(locker, day: str, time_str: str) -> bool:
    if locker.is_24_7:
        return True
    if not locker.weekly_hours:
        return False # don't recommend lockers with unknown hours
    for w in locker.weekly_hours:
        if w["day"] == day and w["start"] <= time_str <= w["end"]:
            return True
    return False