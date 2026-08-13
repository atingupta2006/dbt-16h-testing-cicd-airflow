"""DAG 2 — task order (validate → quarantine → publish).

Purpose
  Show that arrows (>>) mean “must finish before the next step.”

Flow
  1) validate_raw_files   — required CSVs exist and have rows
  2) quarantine_bad_rows  — split zero/blank payments into quarantine vs clean
  3) publish_raw_ready    — write a RAW_READY marker file

Outputs land under AIRFLOW_HOME/olist_work/.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from olist_demo_io import REQUIRED_RAW, read_csv, sample_dir, work_dir, write_csv


def validate_raw_files() -> str:
    """Confirm each required CSV exists and has at least one data row."""
    raw = sample_dir()
    report = {}
    for name in REQUIRED_RAW:
        path = raw / name
        if not path.is_file():
            raise FileNotFoundError(f"Required file missing: {path}")
        rows = read_csv(path)
        if not rows:
            raise ValueError(f"No data rows in {path}")
        report[name] = {"rows": len(rows), "columns": list(rows[0].keys())}

    out = work_dir() / "validate_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    msg = f"Validated {len(report)} files → {out}"
    print(msg)
    return msg


def quarantine_bad_rows() -> str:
    """Put bad payment rows aside; keep good rows for the next step."""
    payments = read_csv(sample_dir() / "payments.csv")
    good: list[dict[str, str]] = []
    bad: list[dict[str, str]] = []

    for row in payments:
        raw_val = (row.get("payment_value") or "").strip()
        try:
            value = float(raw_val) if raw_val else 0.0
        except ValueError:
            # Non-numeric value → treat as bad
            bad.append(row)
            continue
        if value <= 0:
            bad.append(row)
        else:
            good.append(row)

    fields = list(payments[0].keys())
    q_path = work_dir() / "quarantine_zero_payments.csv"
    clean_path = work_dir() / "payments_clean.csv"
    write_csv(q_path, bad, fields)
    write_csv(clean_path, good, fields)

    msg = f"Quarantined {len(bad)} row(s) → {q_path}; clean {len(good)} → {clean_path}"
    print(msg)
    return msg


def publish_raw_ready() -> str:
    """Write a small marker file that says RAW prep is done."""
    marker = work_dir() / "RAW_READY"
    marker.write_text(
        f"ready_at_utc={datetime.utcnow().isoformat()}Z\n"
        f"validate_report={work_dir() / 'validate_report.json'}\n"
        f"payments_clean={work_dir() / 'payments_clean.csv'}\n",
        encoding="utf-8",
    )
    msg = f"Published marker {marker}"
    print(msg)
    return msg


default_args = {
    "owner": "data-team",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="demo_task_order",
    description="Olist: validate RAW → quarantine → publish ready (ordered)",
    start_date=datetime(2024, 1, 1),
    schedule=None,  # run only when Triggered (no cron)
    catchup=False,
    default_args=default_args,
    tags=["demo", "airflow", "olist"],
) as dag:

    validate = PythonOperator(
        task_id="validate_raw_files",
        python_callable=validate_raw_files,
    )
    quarantine = PythonOperator(
        task_id="quarantine_bad_rows",
        python_callable=quarantine_bad_rows,
    )
    publish = PythonOperator(
        task_id="publish_raw_ready",
        python_callable=publish_raw_ready,
    )

    # >> = dependency: left must succeed before right starts
    validate >> quarantine >> publish
