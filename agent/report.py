import os
from dotenv import load_dotenv

load_dotenv()


def generate_report(
    goal,
    metrics,
    evidence,
    investigated
):
    """
    Generate the final investigation report.

    Uses Groq when GROQ_API_KEY is available.
    Otherwise returns a deterministic fallback report.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return fallback_report(
            goal,
            metrics,
            evidence,
            investigated
        )

    try:
        from groq import Groq

        client = Groq(
            api_key=api_key
        )

        model = os.getenv(
            "GROQ_MODEL",
            "llama-3.1-8b-instant"
        )

        prompt = f"""
You are a business revenue investigation assistant.

Business question:
{goal}

Observed metrics:
{metrics}

Investigation evidence:
{evidence}

Investigated hypotheses:
{investigated}

Write a concise business investigation report.

Requirements:
1. State the observed revenue change.
2. Identify the strongest supported explanation.
3. Explain the evidence.
4. Mention other contributing signals.
5. Clearly distinguish observed evidence from interpretation.
6. Do not invent facts.
7. Do not claim causality unless the supplied data proves causality.
8. Mention uncertainty and limitations.
9. Recommend practical next checks.

Use clear headings.
"""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.0,
        )

        return response.choices[0].message.content

    except Exception as exc:
        fallback = fallback_report(
            goal,
            metrics,
            evidence,
            investigated
        )

        return (
            fallback
            + "\n\nGroq report generation failed: "
            + str(exc)
        )


def fallback_report(
    goal,
    metrics,
    evidence,
    investigated
):
    revenue_change = metrics.get(
        "revenue_change_pct",
        0.0
    )

    revenue_change_text = (
        f"{revenue_change:.2f}%"
    )

    lines = []

    lines.append(
        "# Revenue Investigation Report"
    )

    lines.append("")
    lines.append(
        f"**Business question:** {goal}"
    )

    lines.append("")
    lines.append("## Revenue impact")

    lines.append(
        f"Revenue changed by "
        f"**{revenue_change_text}** "
        f"between the baseline and incident periods."
    )

    lines.append("")
    lines.append("## Key observed signals")

    for key, value in metrics.items():

        if key.endswith("_pct"):

            try:
                lines.append(
                    f"- {key}: {float(value):.2f}%"
                )
            except (TypeError, ValueError):
                pass

    lines.append("")
    lines.append("## Investigation")

    if evidence:

        for item in evidence:

            hypothesis = item.get(
                "hypothesis",
                "unknown"
            )

            confidence = item.get(
                "confidence",
                0.0
            )

            lines.append(
                f"- **{hypothesis}** "
                f"(confidence: {confidence:.2f})"
            )

            reasons = item.get(
                "reasons",
                []
            )

            for reason in reasons:
                lines.append(
                    f"  - {reason}"
                )

    lines.append("")
    lines.append("## Investigated hypotheses")

    for hypothesis in investigated:
        lines.append(
            f"- {hypothesis}"
        )

    lines.append("")
    lines.append("## Interpretation")

    if evidence:
        strongest = max(
            evidence,
            key=lambda x: x.get(
                "confidence",
                0.0
            )
        )

        lines.append(
            f"The investigation found the strongest "
            f"supporting evidence for the "
            f"**{strongest.get('hypothesis', 'unknown')}** "
            f"hypothesis."
        )

        lines.append(
            "This should be treated as an evidence-based "
            "explanation rather than proof of causality."
        )
    else:
        lines.append(
            "Insufficient evidence was collected."
        )

    lines.append("")
    lines.append("## Recommended next checks")

    lines.append(
        "- Compare the affected period with the previous period."
    )

    lines.append(
        "- Inspect relevant application and transaction logs."
    )

    lines.append(
        "- Check recent deployments or configuration changes."
    )

    lines.append(
        "- Segment the affected metric by device, "
        "traffic source, product, and payment method."
    )

    return "\n".join(lines)