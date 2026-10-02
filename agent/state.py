from typing import TypedDict, Any


class AgentState(TypedDict, total=False):
    goal: str
    metrics: dict[str, Any]
    selected_hypothesis: str
    strategy_scores: dict[str, float]
    evidence: list[dict[str, Any]]
    investigated: list[str]
    root_cause: str
    confidence: float
    evidence_reasons: list[str]
    status: str
    final_report: str
    report: str