#!/usr/bin/env python3
"""Summarize paired control/treatment live-eval run records."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_records(paths: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            raise ValueError(f"cannot read {path}: {exc}") from exc
        for lineno, raw in enumerate(lines, start=1):
            if not raw.strip():
                continue
            try:
                item = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{lineno}: invalid JSON: {exc}") from exc
            if not isinstance(item, dict) or not item.get("scenario_id") or not item.get("mode"):
                raise ValueError(f"{path}:{lineno}: invalid live-eval record")
            records.append(item)
    return records


def _mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def summarize(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[(str(record.get("provider", "unknown")), str(record.get("model") or "default"), str(record["scenario_id"]))].append(record)

    rows: list[dict[str, Any]] = []
    for (provider, model, scenario), items in sorted(groups.items()):
        arms: dict[str, list[dict[str, Any]]] = {"control": [], "treatment": []}
        for item in items:
            mode = str(item.get("mode"))
            if mode in arms and item.get("status") == "completed":
                arms[mode].append(item)
        control_scores = [float(x.get("score_fraction", 0.0)) for x in arms["control"]]
        treatment_scores = [float(x.get("score_fraction", 0.0)) for x in arms["treatment"]]
        control_mean = _mean(control_scores)
        treatment_mean = _mean(treatment_scores)
        paired: list[float] = []
        by_run: dict[int, dict[str, float]] = defaultdict(dict)
        for item in arms["control"] + arms["treatment"]:
            by_run[int(item.get("run", 0))][str(item["mode"])] = float(item.get("score_fraction", 0.0))
        for values in by_run.values():
            if "control" in values and "treatment" in values:
                paired.append(values["treatment"] - values["control"])
        delta = None if control_mean is None or treatment_mean is None else treatment_mean - control_mean
        threshold = max((float(x.get("pass_threshold", 0.8)) for x in items), default=0.8)
        if delta is None:
            classification = "inconclusive"
        elif delta < -0.02:
            classification = "regressed"
        elif delta > 0.02:
            classification = "improved"
        elif treatment_mean >= threshold and control_mean >= threshold:
            classification = "neutral-good"
        else:
            classification = "no-material-improvement"
        def usage_mean(arm: str, key: str) -> float | None:
            values = [float(x.get("usage", {}).get(key)) for x in arms[arm] if isinstance(x.get("usage", {}).get(key), (int, float))]
            return _mean(values)

        rows.append(
            {
                "provider": provider,
                "model": model,
                "scenario_id": scenario,
                "control_runs": len(control_scores),
                "treatment_runs": len(treatment_scores),
                "control_mean": control_mean,
                "treatment_mean": treatment_mean,
                "mean_delta": delta,
                "paired_mean_delta": _mean(paired),
                "control_pass_rate": _mean([1.0 if x.get("passed") else 0.0 for x in arms["control"]]),
                "treatment_pass_rate": _mean([1.0 if x.get("passed") else 0.0 for x in arms["treatment"]]),
                "control_duration_s": _mean([float(x.get("duration_seconds", 0.0)) for x in arms["control"]]),
                "treatment_duration_s": _mean([float(x.get("duration_seconds", 0.0)) for x in arms["treatment"]]),
                "control_input_tokens": usage_mean("control", "input_tokens"),
                "treatment_input_tokens": usage_mean("treatment", "input_tokens"),
                "control_output_tokens": usage_mean("control", "output_tokens"),
                "treatment_output_tokens": usage_mean("treatment", "output_tokens"),
                "control_cost_usd": usage_mean("control", "total_cost_usd") or usage_mean("control", "cost_usd"),
                "treatment_cost_usd": usage_mean("treatment", "total_cost_usd") or usage_mean("treatment", "cost_usd"),
                "control_changed_files": _mean([float(x.get("workflow_metrics", {}).get("changed_file_count", 0)) for x in arms["control"]]),
                "treatment_changed_files": _mean([float(x.get("workflow_metrics", {}).get("changed_file_count", 0)) for x in arms["treatment"]]),
                "control_diff_churn": _mean([float(x.get("workflow_metrics", {}).get("diff_churn", 0)) for x in arms["control"]]),
                "treatment_diff_churn": _mean([float(x.get("workflow_metrics", {}).get("diff_churn", 0)) for x in arms["treatment"]]),
                "control_unrelated_files": _mean([float(x.get("workflow_metrics", {}).get("unrelated_file_count", 0)) for x in arms["control"] if x.get("workflow_metrics", {}).get("unrelated_file_count") is not None]),
                "treatment_unrelated_files": _mean([float(x.get("workflow_metrics", {}).get("unrelated_file_count", 0)) for x in arms["treatment"] if x.get("workflow_metrics", {}).get("unrelated_file_count") is not None]),
                "control_tool_events": _mean([float(x.get("workflow_metrics", {}).get("tool_event_count", 0)) for x in arms["control"]]),
                "treatment_tool_events": _mean([float(x.get("workflow_metrics", {}).get("tool_event_count", 0)) for x in arms["treatment"]]),
                "classification": classification,
                "manual_checks": sorted({str(check) for x in items for check in x.get("manual_checks", []) if str(check).strip()}),
            }
        )
    return rows


def render_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Live Skill Evaluation Report",
        "",
        "| Provider | Model | Scenario | Control | Treatment | Delta | Pass rate C/T | Result |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        def pct(value: float | None) -> str:
            return "n/a" if value is None else f"{value:.1%}"
        delta = row["mean_delta"]
        lines.append(
            f"| {row['provider']} | {row['model']} | {row['scenario_id']} | {pct(row['control_mean'])} | "
            f"{pct(row['treatment_mean'])} | {('n/a' if delta is None else f'{delta:+.1%}')} | "
            f"{pct(row['control_pass_rate'])} / {pct(row['treatment_pass_rate'])} | {row['classification']} |"
        )
    lines += ["", "## Observed overhead", "", "| Provider | Model | Scenario | Duration C/T | Input tokens C/T | Output tokens C/T | Cost USD C/T |", "| --- | --- | --- | ---: | ---: | ---: | ---: |"]
    for row in rows:
        def num(value: float | None, digits: int = 1) -> str:
            return "n/a" if value is None else f"{value:.{digits}f}"
        lines.append(
            f"| {row['provider']} | {row['model']} | {row['scenario_id']} | "
            f"{num(row['control_duration_s'])} / {num(row['treatment_duration_s'])} | "
            f"{num(row['control_input_tokens'], 0)} / {num(row['treatment_input_tokens'], 0)} | "
            f"{num(row['control_output_tokens'], 0)} / {num(row['treatment_output_tokens'], 0)} | "
            f"{num(row['control_cost_usd'], 4)} / {num(row['treatment_cost_usd'], 4)} |"
        )
    lines += ["", "## Workflow friction signals", "", "| Provider | Model | Scenario | Changed files C/T | Churn C/T | Unrelated files C/T | Tool events C/T |", "| --- | --- | --- | ---: | ---: | ---: | ---: |"]
    for row in rows:
        def metric(value: float | None) -> str:
            return "n/a" if value is None else f"{value:.1f}"
        lines.append(
            f"| {row['provider']} | {row['model']} | {row['scenario_id']} | "
            f"{metric(row['control_changed_files'])} / {metric(row['treatment_changed_files'])} | "
            f"{metric(row['control_diff_churn'])} / {metric(row['treatment_diff_churn'])} | "
            f"{metric(row['control_unrelated_files'])} / {metric(row['treatment_unrelated_files'])} | "
            f"{metric(row['control_tool_events'])} / {metric(row['treatment_tool_events'])} |"
        )
    manual_rows = [row for row in rows if row.get("manual_checks")]
    if manual_rows:
        lines += ["", "## Manual semantic checks", ""]
        for row in manual_rows:
            lines.append(f"**{row['provider']} / {row['model']} / {row['scenario_id']}**")
            for check in row["manual_checks"]:
                lines.append(f"- {check}")
            lines.append("")
    regressions = [row for row in rows if row["classification"] == "regressed"]
    lines += [f"Regressions: **{len(regressions)}**", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize live RED/GREEN skill-eval JSONL records.")
    parser.add_argument("records", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--fail-on-regression", action="store_true")
    args = parser.parse_args(argv)
    try:
        rows = summarize(load_records(args.records))
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2
    text = json.dumps(rows, indent=2) + "\n" if args.json else render_markdown(rows)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8", newline="\n")
        print(f"[OK] Wrote report to {args.output}")
    else:
        sys.stdout.write(text)
    return 1 if args.fail_on_regression and any(row["classification"] == "regressed" for row in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
