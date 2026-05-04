def build_warnings(locker, n_total, n_matching) -> list[str]:
    out = []

    if n_total == 0:
        out.append(
            "This locker has no fallback within walking distance. "
            "If it's full when you arrive, the nearest alternative is more than 300m away."
        )
    elif n_matching == 0:
        out.append(
            "If this locker is full, none of its nearby alternatives match your filters."
        )

    if not locker.is_24_7 and not locker.weekly_hours:
        out.append(
            "Opening hours not published for this locker. Verify in the InPost app before going."
        )

    if locker.location_type == "Indoor":
        out.append(
            "This locker is inside a building. You'll need to enter a building to access it."
        )

    return out