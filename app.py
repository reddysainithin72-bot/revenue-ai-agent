import streamlit as st

from agent.graph import build_graph


st.set_page_config(
    page_title="AI Revenue Root-Cause Agent",
    page_icon="📊",
    layout="wide",
)

st.title("📊 AI Revenue Root-Cause Investigation Agent")
st.write(
    "Use LangGraph + NEAT to investigate why business revenue changed."
)

goal = st.text_area(
    "Investigation goal",
    value="Our total revenue dropped last month. Find out why.",
    height=100,
)

if st.button("🚀 Start Investigation", type="primary"):

    with st.spinner("Investigating revenue..."):

        try:
            graph = build_graph()

            result = graph.invoke(
                {
                    "goal": goal,
                    "investigated": [],
                }
            )

        except Exception as e:
            st.error("Investigation failed.")
            st.exception(e)
            st.stop()

    st.success("Investigation completed!")

    # -------------------------
    # Main results
    # -------------------------

    metrics = result.get("metrics", {})
    root_cause = result.get(
        "root_cause",
        result.get("selected_hypothesis", "unknown")
    )

    investigated = result.get("investigated", [])
    strategy_scores = result.get("strategy_scores", {})
    evidence = result.get("evidence", [])

    # -------------------------
    # Summary
    # -------------------------

    st.subheader("🔎 Investigation Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Revenue Change",
            f"{metrics.get('revenue_change_pct', 0):.2f}%"
        )

    with col2:
        st.metric(
            "Root-Cause Hypothesis",
            str(root_cause).title()
        )

    with col3:
        st.metric(
            "Investigations",
            len(investigated)
        )

    # -------------------------
    # Metrics
    # -------------------------

    st.subheader("📈 Business Metrics")

    metric_cols = st.columns(3)

    metric_data = [
        ("Revenue", "revenue_change_pct"),
        ("Traffic", "traffic_change_pct"),
        ("Conversion", "conversion_change_pct"),
        ("Mobile Conversion", "mobile_conversion_change_pct"),
        ("Payment Failure", "payment_failure_change_pct"),
        ("Checkout Errors", "checkout_error_change_pct"),
    ]

    for i, (label, key) in enumerate(metric_data):

        with metric_cols[i % 3]:

            value = metrics.get(key, 0)

            st.metric(
                label,
                f"{value:.2f}%"
            )

    # -------------------------
    # NEAT strategy
    # -------------------------

    st.subheader("🧠 NEAT Investigation Strategy")

    if strategy_scores:

        for hypothesis, score in strategy_scores.items():

            st.write(
                f"**{hypothesis.title()}** — "
                f"{score:.2f}"
            )

            st.progress(
                min(max(float(score) / 200.0, 0.0), 1.0)
            )

    # -------------------------
    # Investigated hypotheses
    # -------------------------

    st.subheader("🔬 Investigated Hypotheses")

    if investigated:

        for hypothesis in investigated:
            st.write(f"✅ {hypothesis.title()}")

    else:
        st.info("No hypotheses recorded.")

    # -------------------------
    # Evidence
    # -------------------------

    st.subheader("📋 Evidence")

    if evidence:

        for i, item in enumerate(evidence, 1):

            hypothesis = item.get(
                "hypothesis",
                "unknown"
            )

            confidence = item.get(
                "confidence",
                0
            )

            reasons = item.get(
                "reasons",
                []
            )

            with st.expander(
                f"{i}. {hypothesis.title()} "
                f"| Confidence: {confidence:.0%}"
            ):

                if reasons:

                    for reason in reasons:
                        st.write(f"• {reason}")

                raw_evidence = item.get(
                    "raw_evidence"
                )

                if raw_evidence:
                    st.json(raw_evidence)

    else:
        st.info("No evidence returned.")

    # -------------------------
    # Final report
    # -------------------------

    st.subheader("📝 AI Investigation Report")

    report = result.get(
        "final_report",
        result.get("report", "")
    )

    if report:

        st.markdown(report)

    else:

        st.warning(
            "The investigation completed, but no final report was returned."
        )

    # -------------------------
    # Raw state
    # -------------------------

    with st.expander("🔧 View Agent State"):

        st.json(result)