from lockers.ingest.hours import parse_hours, _minutes_to_time


def test_none_input():
    out, ok = parse_hours(None)
    assert not ok and out == []


def test_no_customer_key():
    out, ok = parse_hours({"customer": None})
    assert not ok and out == []


def test_empty_customer():
    out, ok = parse_hours({"customer": {}})
    assert not ok and out == []


def test_weekday_only():
    extended = {"customer": {
        "monday": [{"start": 540, "end": 1080}],
        "tuesday": [{"start": 540, "end": 1080}],
        "wednesday": [{"start": 540, "end": 1080}],
        "thursday": [{"start": 540, "end": 1080}],
        "friday": [{"start": 540, "end": 1080}],
        "saturday": [],
        "sunday": [],
    }}
    out, ok = parse_hours(extended)
    assert ok
    assert {w["day"] for w in out} == {"mon", "tue", "wed", "thu", "fri"}
    assert all(w["start"] == "09:00" and w["end"] == "18:00" for w in out)


def test_split_shifts_same_day():
    extended = {"customer": {"monday": [
        {"start": 480, "end": 720},
        {"start": 840, "end": 1080},
    ]}}
    out, ok = parse_hours(extended)
    assert ok
    assert len(out) == 2
    assert out[0] == {"day": "mon", "start": "08:00", "end": "12:00"}
    assert out[1] == {"day": "mon", "start": "14:00", "end": "18:00"}


def test_unknown_day_skipped():
    extended = {"customer": {"funday": [{"start": 0, "end": 1440}]}}
    out, ok = parse_hours(extended)
    assert not ok and out == []


def test_minutes_to_time():
    assert _minutes_to_time(0) == "00:00"
    assert _minutes_to_time(540) == "09:00"
    assert _minutes_to_time(1080) == "18:00"
    assert _minutes_to_time(1439) == "23:59"