from lockers.recommender.filters import FilterSet, matches


class FakeLocker:
    def __init__(self, **kw):
        self.is_24_7 = kw.get("is_24_7", False)
        self.easy_access = kw.get("easy_access", False)
        self.weekly_hours = kw.get("weekly_hours", [])


def test_passes_when_no_filters():
    assert matches(FakeLocker(), FilterSet())


def test_require_24_7_blocks_non_24_7():
    f = FilterSet(require_24_7=True)
    assert not matches(FakeLocker(is_24_7=False), f)
    assert matches(FakeLocker(is_24_7=True), f)


def test_require_easy_access():
    f = FilterSet(require_easy_access=True)
    assert not matches(FakeLocker(easy_access=False), f)
    assert matches(FakeLocker(easy_access=True), f)


def test_open_at_within_window():
    f = FilterSet(open_at_day="mon", open_at_time="10:00")
    L = FakeLocker(weekly_hours=[{"day": "mon", "start": "08:00", "end": "16:00"}])
    assert matches(L, f)


def test_open_at_outside_window():
    f = FilterSet(open_at_day="mon", open_at_time="22:00")
    L = FakeLocker(weekly_hours=[{"day": "mon", "start": "08:00", "end": "16:00"}])
    assert not matches(L, f)


def test_open_at_unknown_hours_excluded():
    """Honest fallback: don't recommend lockers we don't know the hours of."""
    f = FilterSet(open_at_day="mon", open_at_time="10:00")
    assert not matches(FakeLocker(weekly_hours=[]), f)


def test_open_at_24_7_always_passes():
    f = FilterSet(open_at_day="sun", open_at_time="03:00")
    assert matches(FakeLocker(is_24_7=True), f)