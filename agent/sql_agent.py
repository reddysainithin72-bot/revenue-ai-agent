from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


def _load_data(csv_path=None):

    # -----------------------------------------
    # Production mode: uploaded company CSV
    # -----------------------------------------

    if csv_path:

        path = Path(csv_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Company CSV not found: {path}"
            )

        df = pd.read_csv(path)

        df.columns = [
            str(column)
            .strip()
            .lower()
            .replace(" ", "_")
            for column in df.columns
        ]

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        return df

    # -----------------------------------------
    # Test/development mode: SQLite
    # -----------------------------------------

    from database.schema import DB_PATH

    db_path = Path(DB_PATH)

    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found: {db_path}"
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

        if "payments" in table_names:

            return pd.read_sql_query(
                "SELECT * FROM payments",
                conn,
            )

        raise ValueError(
            "No supported table found in database."
        )


def investigate(
    hypothesis: str,
    csv_path: str | None = None,
):

    # -----------------------------------------
    # Legacy SQLite test mode
    # -----------------------------------------

    if csv_path is None:

        df = _load_data()

        if hypothesis == "payment":

            if "status" in df.columns:

                failures = (
                    df["status"]
                    .astype(str)
                    .str.lower()
                    .eq("failed")
                    .sum()
                )

                return {
                    "hypothesis": "payment",
                    "total_records": len(df),
                    "failed_payments":
                        int(failures),
                }

            if "payment_status" in df.columns:

                failures = (
                    df["payment_status"]
                    .astype(str)
                    .str.lower()
                    .eq("failed")
                    .sum()
                )

                return {
                    "hypothesis": "payment",
                    "total_records": len(df),
                    "failed_payments":
                        int(failures),
                }

            return {
                "hypothesis": "payment",
                "total_records": len(df),
            }

        return {
            "hypothesis": hypothesis,
            "total_records": len(df),
        }

    # -----------------------------------------
    # CSV investigation mode
    # -----------------------------------------

    df = _load_data(csv_path)

    daily = (
        df.groupby("date", as_index=False)
        .sum(numeric_only=True)
        .sort_values("date")
    )

    if len(daily) < 2:
        raise ValueError(
            "At least two dates are required."
        )

    midpoint = len(daily) // 2

    baseline = daily.iloc[:midpoint]
    incident = daily.iloc[midpoint:]

    # -----------------------------------------
    # Traffic
    # -----------------------------------------

    if hypothesis == "traffic":

        baseline_value = float(
            baseline["sessions"].sum()
        )

        incident_value = float(
            incident["sessions"].sum()
        )

        change = (
            (incident_value - baseline_value)
            / baseline_value
            * 100
            if baseline_value
            else 0
        )

        return {
            "hypothesis": "traffic",
            "baseline_sessions":
                baseline_value,
            "incident_sessions":
                incident_value,
            "change_pct":
                change,
        }

    # -----------------------------------------
    # Conversion
    # -----------------------------------------

    if hypothesis == "conversion":

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

        baseline_rate = (
            baseline_orders / baseline_sessions
            if baseline_sessions
            else 0
        )

        incident_rate = (
            incident_orders / incident_sessions
            if incident_sessions
            else 0
        )

        change = (
            (incident_rate - baseline_rate)
            / baseline_rate
            * 100
            if baseline_rate
            else 0
        )

        return {
            "hypothesis": "conversion",
            "baseline_conversion":
                baseline_rate,
            "incident_conversion":
                incident_rate,
            "change_pct":
                change,
        }

    # -----------------------------------------
    # Device
    # -----------------------------------------

    if hypothesis == "device":

        baseline_sessions = float(
            baseline["mobile_sessions"].sum()
        )

        incident_sessions = float(
            incident["mobile_sessions"].sum()
        )

        baseline_orders = float(
            baseline["mobile_orders"].sum()
        )

        incident_orders = float(
            incident["mobile_orders"].sum()
        )

        baseline_rate = (
            baseline_orders / baseline_sessions
            if baseline_sessions
            else 0
        )

        incident_rate = (
            incident_orders / incident_sessions
            if incident_sessions
            else 0
        )

        change = (
            (incident_rate - baseline_rate)
            / baseline_rate
            * 100
            if baseline_rate
            else 0
        )

        return {
            "hypothesis": "device",
            "baseline_mobile_conversion":
                baseline_rate,
            "incident_mobile_conversion":
                incident_rate,
            "change_pct":
                change,
        }

    # -----------------------------------------
    # Payment
    # -----------------------------------------

    if hypothesis == "payment":

        baseline_attempts = float(
            baseline["payment_attempts"].sum()
        )

        incident_attempts = float(
            incident["payment_attempts"].sum()
        )

        baseline_failures = float(
            baseline["payment_failures"].sum()
        )

        incident_failures = float(
            incident["payment_failures"].sum()
        )

        baseline_rate = (
            baseline_failures
            / baseline_attempts
            if baseline_attempts
            else 0
        )

        incident_rate = (
            incident_failures
            / incident_attempts
            if incident_attempts
            else 0
        )

        change = (
            (incident_rate - baseline_rate)
            / baseline_rate
            * 100
            if baseline_rate
            else 0
        )

        return {
            "hypothesis": "payment",
            "baseline_failure_rate":
                baseline_rate,
            "incident_failure_rate":
                incident_rate,
            "change_pct":
                change,
        }

    # -----------------------------------------
    # Technical
    # -----------------------------------------

    if hypothesis == "technical":

        baseline_errors = float(
            baseline["checkout_errors"].sum()
        )

        incident_errors = float(
            incident["checkout_errors"].sum()
        )

        change = (
            (incident_errors - baseline_errors)
            / baseline_errors
            * 100
            if baseline_errors
            else 0
        )

        return {
            "hypothesis": "technical",
            "baseline_errors":
                baseline_errors,
            "incident_errors":
                incident_errors,
            "change_pct":
                change,
        }

    # -----------------------------------------
    # Product
    # -----------------------------------------

    if hypothesis == "product":

        return {
            "hypothesis": "product",
            "message":
                "Product-level evidence requires "
                "product/category columns."
        }

    return {
        "hypothesis": hypothesis,
        "message":
            "No evidence rule available."
    }