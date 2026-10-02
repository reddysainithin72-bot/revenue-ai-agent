from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_COLUMNS = [
    "date",
    "revenue",
    "sessions",
    "orders",
    "mobile_sessions",
    "mobile_orders",
    "payment_attempts",
    "payment_failures",
    "checkout_errors",
]


def _pct_change(baseline: float, incident: float) -> float:
    if baseline == 0:
        if incident == 0:
            return 0.0
        return 100.0

    return ((incident - baseline) / baseline) * 100.0


def validate_dataframe(df: pd.DataFrame) -> list[str]:
    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    return missing


def load_company_csv(csv_path: str | Path) -> pd.DataFrame:

    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {path}"
        )

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError(
            "The uploaded CSV is empty."
        )

    # Normalize column names
    df.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in df.columns
    ]

    missing = validate_dataframe(df)

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
        )

    # Date
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    if df["date"].isna().all():
        raise ValueError(
            "The 'date' column does not contain valid dates."
        )

    # Numeric columns
    numeric_columns = [
        "revenue",
        "sessions",
        "orders",
        "mobile_sessions",
        "mobile_orders",
        "payment_attempts",
        "payment_failures",
        "checkout_errors",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Remove rows without dates
    df = df.dropna(
        subset=["date"]
    ).copy()

    # Missing numeric values become zero
    for column in numeric_columns:
        df[column] = df[column].fillna(0)

    # Sort chronologically
    df = df.sort_values("date")

    return df


def calculate_metrics_from_dataframe(
    df: pd.DataFrame,
) -> dict[str, Any]:

    if df.empty:
        raise ValueError(
            "No usable rows found in the dataset."
        )

    # Aggregate by date in case the CSV contains
    # multiple records per day.
    daily = (
        df.groupby("date", as_index=False)[
            [
                "revenue",
                "sessions",
                "orders",
                "mobile_sessions",
                "mobile_orders",
                "payment_attempts",
                "payment_failures",
                "checkout_errors",
            ]
        ]
        .sum()
        .sort_values("date")
    )

    if len(daily) < 2:
        raise ValueError(
            "At least two different dates are required "
            "to compare baseline and incident periods."
        )

    midpoint = len(daily) // 2

    baseline = daily.iloc[:midpoint]
    incident = daily.iloc[midpoint:]

    baseline_revenue = float(
        baseline["revenue"].sum()
    )

    incident_revenue = float(
        incident["revenue"].sum()
    )

    baseline_sessions = float(
        baseline["sessions"].sum()
    )

    incident_sessions = float(
        incident["sessions"].sum()
    )

    baseline_orders = float(
        baseline["orders"].sum()
    )

    incident_orders = float(
        incident["orders"].sum()
    )

    baseline_mobile_sessions = float(
        baseline["mobile_sessions"].sum()
    )

    incident_mobile_sessions = float(
        incident["mobile_sessions"].sum()
    )

    baseline_mobile_orders = float(
        baseline["mobile_orders"].sum()
    )

    incident_mobile_orders = float(
        incident["mobile_orders"].sum()
    )

    baseline_payment_attempts = float(
        baseline["payment_attempts"].sum()
    )

    incident_payment_attempts = float(
        incident["payment_attempts"].sum()
    )

    baseline_payment_failures = float(
        baseline["payment_failures"].sum()
    )

    incident_payment_failures = float(
        incident["payment_failures"].sum()
    )

    baseline_errors = float(
        baseline["checkout_errors"].sum()
    )

    incident_errors = float(
        incident["checkout_errors"].sum()
    )

    # Rates
    baseline_conversion = (
        baseline_orders / baseline_sessions
        if baseline_sessions
        else 0.0
    )

    incident_conversion = (
        incident_orders / incident_sessions
        if incident_sessions
        else 0.0
    )

    baseline_mobile_conversion = (
        baseline_mobile_orders
        / baseline_mobile_sessions
        if baseline_mobile_sessions
        else 0.0
    )

    incident_mobile_conversion = (
        incident_mobile_orders
        / incident_mobile_sessions
        if incident_mobile_sessions
        else 0.0
    )

    baseline_payment_failure = (
        baseline_payment_failures
        / baseline_payment_attempts
        if baseline_payment_attempts
        else 0.0
    )

    incident_payment_failure = (
        incident_payment_failures
        / incident_payment_attempts
        if incident_payment_attempts
        else 0.0
    )

    metrics = {

        "status": "metrics_calculated",

        "baseline_start": str(
            baseline["date"].min().date()
        ),

        "baseline_end": str(
            baseline["date"].max().date()
        ),

        "incident_start": str(
            incident["date"].min().date()
        ),

        "incident_end": str(
            incident["date"].max().date()
        ),

        "baseline_revenue": baseline_revenue,
        "incident_revenue": incident_revenue,

        "baseline_sessions": baseline_sessions,
        "incident_sessions": incident_sessions,

        "baseline_orders": baseline_orders,
        "incident_orders": incident_orders,

        "baseline_conversion": baseline_conversion,
        "incident_conversion": incident_conversion,

        "baseline_mobile_conversion":
            baseline_mobile_conversion,

        "incident_mobile_conversion":
            incident_mobile_conversion,

        "baseline_payment_failure":
            baseline_payment_failure,

        "incident_payment_failure":
            incident_payment_failure,

        "baseline_errors": baseline_errors,
        "incident_errors": incident_errors,

        "revenue_change_pct": _pct_change(
            baseline_revenue,
            incident_revenue,
        ),

        "traffic_change_pct": _pct_change(
            baseline_sessions,
            incident_sessions,
        ),

        "conversion_change_pct": _pct_change(
            baseline_conversion,
            incident_conversion,
        ),

        "mobile_conversion_change_pct": _pct_change(
            baseline_mobile_conversion,
            incident_mobile_conversion,
        ),

        "payment_failure_change_pct": _pct_change(
            baseline_payment_failure,
            incident_payment_failure,
        ),

        "checkout_error_change_pct": _pct_change(
            baseline_errors,
            incident_errors,
        ),
    }

    return metrics


def calculate_metrics(
    csv_path: str | Path | None = None,
) -> dict[str, Any]:

    # Production / Streamlit mode:
    # use uploaded company CSV.
    if csv_path is not None:
        df = load_company_csv(csv_path)
        return calculate_metrics_from_dataframe(df)

    # Test / legacy development mode:
    # use the seeded SQLite database.
    from database.schema import DB_PATH

    import sqlite3

    db_path = Path(DB_PATH)

    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found: {db_path}. "
            "Run: python database/seed.py"
        )

    with sqlite3.connect(db_path) as conn:

        tables = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            """,
            conn,
        )

        table_names = set(
            tables["name"].tolist()
        )

        # Existing synthetic project database
        if "daily_metrics" in table_names:

            daily = pd.read_sql_query(
                "SELECT * FROM daily_metrics",
                conn,
            )

            daily.columns = [
                str(c)
                .strip()
                .lower()
                .replace(" ", "_")
                for c in daily.columns
            ]

            if "date" in daily.columns:
                daily["date"] = pd.to_datetime(
                    daily["date"],
                    errors="coerce",
                )

            # Convert the old DB schema into the
            # new dataframe schema.
            rename_map = {
                "traffic": "sessions",
                "conversion": "orders",
                "mobile_traffic": "mobile_sessions",
                "mobile_orders": "mobile_orders",
                "payment_attempts": "payment_attempts",
                "payment_failures": "payment_failures",
                "checkout_errors": "checkout_errors",
            }

            daily = daily.rename(
                columns=rename_map
            )

            # If orders are not explicitly available,
            # derive them from sessions * conversion.
            if (
                "orders" not in daily.columns
                and "sessions" in daily.columns
                and "conversion" in daily.columns
            ):
                daily["orders"] = (
                    daily["sessions"]
                    * daily["conversion"]
                )

            # If mobile_sessions is absent,
            # use total sessions as fallback only
            # for legacy test data.
            if "mobile_sessions" not in daily.columns:
                daily["mobile_sessions"] = (
                    daily["sessions"]
                )

            if "mobile_orders" not in daily.columns:
                daily["mobile_orders"] = (
                    daily["orders"]
                )

            if "payment_attempts" not in daily.columns:
                daily["payment_attempts"] = (
                    daily["sessions"]
                )

            if "payment_failures" not in daily.columns:
                daily["payment_failures"] = 0

            if "checkout_errors" not in daily.columns:
                daily["checkout_errors"] = 0

            required = [
                "date",
                "revenue",
                "sessions",
                "orders",
                "mobile_sessions",
                "mobile_orders",
                "payment_attempts",
                "payment_failures",
                "checkout_errors",
            ]

            missing = [
                column
                for column in required
                if column not in daily.columns
            ]

            if missing:
                raise ValueError(
                    "Legacy database is missing columns: "
                    + ", ".join(missing)
                )

            return calculate_metrics_from_dataframe(
                daily[required]
            )

    raise ValueError(
        "No supported business data found in the database."
    )