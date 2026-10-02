from langgraph.graph import StateGraph, START, END

from .state import AgentState
from .profiler import profile_business
from .sql_agent import investigate
from .evidence import evaluate_evidence
from neat_engine.strategy import choose_strategy
from .report import generate_report


def profile_node(state: AgentState):

    metrics = profile_business(state)

    return {
        "metrics": metrics
    }


def strategy_node(state: AgentState):

    metrics = state.get(
        "metrics",
        {}
    )

    investigated = state.get(
        "investigated",
        []
    )

    result = choose_strategy(
        metrics,
        investigated
    )

    return {
        "selected_hypothesis":
            result["hypothesis"],

        "strategy_scores":
            result["scores"]
    }


def investigation_node(state: AgentState):

    hypothesis = state[
        "selected_hypothesis"
    ]

    csv_path = state.get(
        "csv_path"
    )

    evidence = investigate(
        hypothesis,
        csv_path
    )

    return {
        "evidence": evidence
    }


def evidence_node(state: AgentState):

    hypothesis = state[
        "selected_hypothesis"
    ]

    metrics = state.get(
        "metrics",
        {}
    )

    evidence = state.get(
        "evidence",
        []
    )

    result = evaluate_evidence(
        hypothesis,
        metrics,
        evidence
    )

    investigated = list(
        state.get(
            "investigated",
            []
        )
    )

    if hypothesis not in investigated:

        investigated.append(
            hypothesis
        )

    return {
        "evidence": [result],
        "investigated": investigated
    }


def should_continue(state):

    evidence = state.get(
        "evidence",
        []
    )

    investigated = state.get(
        "investigated",
        []
    )

    if evidence:

        latest = evidence[-1]

        confidence = latest.get(
            "confidence",
            0.0
        )

        if confidence >= 0.90:
            return "final"

    if len(investigated) >= 4:
        return "final"

    return "strategy"


def final_node(state):

    report = generate_report(
        state.get("goal", ""),
        state.get("metrics", {}),
        state.get("evidence", []),
        state.get("investigated", [])
    )

    evidence = state.get(
        "evidence",
        []
    )

    root_cause = None

    if evidence:

        strongest = max(
            evidence,
            key=lambda item:
                item.get(
                    "confidence",
                    0.0
                )
        )

        root_cause = strongest.get(
            "hypothesis"
        )

    return {

        "status":
            "investigation_complete",

        "root_cause":
            root_cause,

        "final_report":
            report,

        "report":
            report
    }


def build_graph():

    graph = StateGraph(
        AgentState
    )

    graph.add_node(
        "profile",
        profile_node
    )

    graph.add_node(
        "strategy",
        strategy_node
    )

    graph.add_node(
        "investigate",
        investigation_node
    )

    graph.add_node(
        "evidence",
        evidence_node
    )

    graph.add_node(
        "final",
        final_node
    )

    graph.add_edge(
        START,
        "profile"
    )

    graph.add_edge(
        "profile",
        "strategy"
    )

    graph.add_edge(
        "strategy",
        "investigate"
    )

    graph.add_edge(
        "investigate",
        "evidence"
    )

    graph.add_conditional_edges(
        "evidence",
        should_continue,
        {
            "strategy": "strategy",
            "final": "final",
        }
    )

    graph.add_edge(
        "final",
        END
    )

    return graph.compile()