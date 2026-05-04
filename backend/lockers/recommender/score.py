from dataclasses import dataclass

R_ANCHOR_M = 500

@dataclass
class ScoreBreakdown:
    proximity: float
    fallback_robustness: float
    total: float

def score_candidate(
    distance_m: float,
    n_total_neighbors: int,
    n_matching_neighbors: int,
) -> ScoreBreakdown:
    proximity = max(0.0, 1.0 - distance_m / R_ANCHOR_M)
    fallback = (
        min(1.0, n_matching_neighbors / n_total_neighbors)
        if n_total_neighbors > 0 else 0.0
    )
    total = 0.50 * proximity + 0.50 * fallback
    return ScoreBreakdown(proximity, fallback, total)