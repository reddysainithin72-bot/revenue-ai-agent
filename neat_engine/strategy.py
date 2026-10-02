from .features import normalize_metrics

HYPOTHESES = [
    "traffic",
    "conversion",
    "device",
    "product",
    "payment",
    "technical",
]


def choose_strategy(metrics, investigated=None):
    """
    Select the next revenue investigation hypothesis.

    Returns:
        {
            "hypothesis": "...",
            "scores": {...}
        }
    """

    investigated = investigated or []

    scores = {
        "traffic": 0.0,
        "conversion": 0.0,
        "device": 0.0,
        "product": 0.1,
        "payment": 0.0,
        "technical": 0.0,
    }

    # Traffic signal
    traffic_change = metrics.get(
        "traffic_change_pct",
        0.0
    )

    if traffic_change < -10:
        scores["traffic"] += abs(traffic_change)

    # Conversion signal
    conversion_change = metrics.get(
        "conversion_change_pct",
        0.0
    )

    if conversion_change < -10:
        scores["conversion"] += abs(
            conversion_change
        )

    # Mobile/device signal
    mobile_change = metrics.get(
        "mobile_conversion_change_pct",
        0.0
    )

    if mobile_change < -15:
        scores["device"] += abs(
            mobile_change
        )

    # Payment signal
    payment_change = metrics.get(
        "payment_failure_change_pct",
        0.0
    )

    if payment_change > 20:
        scores["payment"] += payment_change

    # Technical signal
    error_change = metrics.get(
        "checkout_error_change_pct",
        0.0
    )

    if error_change > 20:
        scores["technical"] += error_change

    # Prevent already-investigated hypotheses
    available = {
        hypothesis: score
        for hypothesis, score in scores.items()
        if hypothesis not in investigated
    }

    # If everything has already been investigated
    if not available:
        return {
            "hypothesis": "technical",
            "scores": scores,
        }

    best = max(
        available,
        key=available.get
    )

    return {
        "hypothesis": best,
        "scores": scores,
    }