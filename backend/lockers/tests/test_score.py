from lockers.recommender.score import score_candidate


def test_close_with_robust_fallback_scores_high():
    s = score_candidate(distance_m=100, n_total_neighbors=3, n_matching_neighbors=3)
    assert s.proximity > 0.7
    assert s.fallback_robustness == 1.0
    assert s.total > 0.6


def test_no_neighbors_zero_fallback():
    s = score_candidate(distance_m=50, n_total_neighbors=0, n_matching_neighbors=0)
    assert s.fallback_robustness == 0.0


def test_robust_fallback_outranks_proximity():
    """The central design test: robust fallback set beats raw proximity."""
    closer_fragile = score_candidate(50, 3, 0)
    farther_robust = score_candidate(200, 3, 3)
    assert farther_robust.total > closer_fragile.total


def test_distance_beyond_radius_zero_proximity():
    s = score_candidate(distance_m=600, n_total_neighbors=2, n_matching_neighbors=2)
    assert s.proximity == 0.0