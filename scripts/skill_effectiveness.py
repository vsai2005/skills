#!/usr/bin/env python3
"""Build statistically qualified, version-bound skill-effectiveness evidence."""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    from scripts.empirical_stats import bootstrap_mean_ci, exact_sign_test_pvalue, median, win_rate
    from scripts.eval_provenance import sha256_tree
except ModuleNotFoundError:
    from empirical_stats import bootstrap_mean_ci, exact_sign_test_pvalue, median, win_rate
    from eval_provenance import sha256_tree


def load_records(paths: Path | list[Path]) -> list[dict[str, Any]]:
    if isinstance(paths, Path):
        paths = [paths]
    out: list[dict[str, Any]] = []
    for path in paths:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{n}: invalid JSONL: {exc}") from exc
            if item.get("mode") not in {"control", "treatment"}:
                continue
            if item.get("status") != "completed":
                continue
            out.append(item)
    return out


def num(record: dict[str, Any], key: str) -> float | None:
    value = record.get(key)
    if isinstance(value, (int, float)):
        return float(value)
    if key in {"tokens", "cost"}:
        usage = record.get("usage") or {}
        candidates = {
            "tokens": ["total_tokens", "tokens"],
            "cost": ["cost_usd", "total_cost_usd"],
        }[key]
        for candidate in candidates:
            if isinstance(usage.get(candidate), (int, float)):
                return float(usage[candidate])
        if key == "tokens":
            inp = usage.get("input_tokens")
            out = usage.get("output_tokens")
            if isinstance(inp, (int, float)) and isinstance(out, (int, float)):
                return float(inp) + float(out)
    if key in {"churn", "unrelated_files"}:
        workflow = record.get("workflow_metrics") or {}
        metric = {"churn": "diff_churn", "unrelated_files": "unrelated_file_count"}[key]
        if isinstance(workflow.get(metric), (int, float)):
            return float(workflow[metric])
    return None


def _avg(values: list[float]) -> float | None:
    return round(statistics.fmean(values), 6) if values else None


def _ratio(controls: list[dict[str, Any]], treatments: list[dict[str, Any]], metric: str) -> float | None:
    c = [value for record in controls if (value := num(record, metric)) is not None]
    t = [value for record in treatments if (value := num(record, metric)) is not None]
    ca, ta = _avg(c), _avg(t)
    if ca is None or ta is None or ca <= 0:
        return None
    return round(ta / ca, 6)


def classify(
    score_delta: float,
    token_ratio: float | None,
    time_ratio: float | None,
    *,
    ci_low: float | None = None,
    ci_high: float | None = None,
    min_effect: float = 0.05,
    costly_ratio: float = 1.5,
) -> str:
    """Classify evidence conservatively; strong claims require CI separation from zero."""
    expensive = any(r is not None and r >= costly_ratio for r in (token_ratio, time_ratio))
    if ci_low is None or ci_high is None:
        if score_delta <= -0.05:
            return "HARMFUL"
        if score_delta >= 0.08:
            return "COSTLY" if expensive and score_delta < 0.20 else "BENEFICIAL"
        if expensive:
            return "COSTLY"
        return "NEUTRAL"
    if ci_high < -min_effect:
        return "HARMFUL"
    if ci_low is not None and ci_low > min_effect:
        return "COSTLY" if expensive and score_delta < 0.20 else "BENEFICIAL"
    if score_delta <= -min_effect:
        return "POSSIBLY_HARMFUL"
    if score_delta >= min_effect:
        return "COSTLY" if expensive else "PROMISING"
    if expensive:
        return "COSTLY"
    return "NEUTRAL"


def _pair_records(records: list[dict[str, Any]]) -> dict[tuple[str, str, str, str, str, str], tuple[dict[str, Any], dict[str, Any]]]:
    attempts: dict[tuple[str, str, str, str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        campaign = str(record.get("campaign_id") or "legacy")
        provider = str(record.get("provider") or "unknown")
        model = str(record.get("model") or "default")
        scenario = str(record.get("scenario_id") or "unknown")
        run = str(record.get("run") or "0")
        case_hash = str(record.get("case_sha256") or "legacy-case")
        attempts[(campaign, provider, model, scenario, run, case_hash)][str(record["mode"])] = record
    paired = {}
    for key, arms in attempts.items():
        if "control" in arms and "treatment" in arms:
            paired[key] = (arms["control"], arms["treatment"])
    return paired


def build_registry(
    records: list[dict[str, Any]],
    min_pairs: int = 5,
    *,
    confidence: float = 0.95,
    bootstrap_samples: int = 5000,
    min_effect: float = 0.05,
    costly_ratio: float = 1.5,
) -> dict[str, Any]:
    paired = _pair_records(records)
    grouped: dict[tuple[str, str, str, str], list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for (_campaign, provider, model, _scenario, _run, _case_hash), (control, treatment) in paired.items():
        skill = str(treatment.get("skill") or control.get("skill") or "unknown")
        treatment_hash = str((treatment.get("skill_hashes") or {}).get(skill) or treatment.get("skill_sha256") or "legacy-skill")
        control_hash = str((control.get("skill_hashes") or {}).get(skill) or control.get("skill_sha256") or treatment_hash)
        skill_hash = treatment_hash if treatment_hash == control_hash else f"mixed:{control_hash}:{treatment_hash}"
        grouped[(provider, model, skill, skill_hash)].append((control, treatment))

    entries: list[dict[str, Any]] = []
    for (provider, model, skill, skill_hash), pairs_list in sorted(grouped.items()):
        controls = [c for c, _ in pairs_list]
        treatments = [t for _, t in pairs_list]
        deltas = [float(t.get("score_fraction", 0.0)) - float(c.get("score_fraction", 0.0)) for c, t in pairs_list]
        pair_count = len(deltas)
        control_scores = [float(r.get("score_fraction", 0.0)) for r in controls]
        treatment_scores = [float(r.get("score_fraction", 0.0)) for r in treatments]
        control_avg = _avg(control_scores) or 0.0
        treatment_avg = _avg(treatment_scores) or 0.0
        delta = round((statistics.fmean(deltas) if deltas else 0.0), 6)
        ci_low, ci_high = bootstrap_mean_ci(deltas, confidence=confidence, samples=bootstrap_samples, seed=0) if deltas else (None, None)
        token_ratio = _ratio(controls, treatments, "tokens")
        time_ratio = _ratio(controls, treatments, "duration_seconds")
        if pair_count < min_pairs or skill_hash.startswith("mixed:"):
            classification = "INSUFFICIENT_DATA"
        else:
            classification = classify(
                delta, token_ratio, time_ratio, ci_low=ci_low, ci_high=ci_high,
                min_effect=min_effect, costly_ratio=costly_ratio,
            )
        sign_p = exact_sign_test_pvalue(deltas)
        strong = pair_count >= min_pairs and classification in {"BENEFICIAL", "HARMFUL"} and ci_low is not None and ci_high is not None
        entries.append({
            "provider": provider,
            "model": model,
            "skill": skill,
            "skill_sha256": skill_hash,
            "pairs": pair_count,
            "campaigns": sorted({str(r.get("campaign_id") or "legacy") for r in controls + treatments}),
            "case_versions": sorted({str(r.get("case_sha256") or "legacy-case") for r in controls + treatments}),
            "classification": classification,
            "strong_evidence": strong,
            "control_score": control_avg,
            "treatment_score": treatment_avg,
            "score_delta": delta,
            "paired_median_delta": median(deltas),
            "bootstrap_ci": [ci_low, ci_high],
            "confidence": confidence,
            "sign_test_p": sign_p,
            "win_rate": win_rate(deltas),
            "control_pass_rate": _avg([1.0 if r.get("passed") else 0.0 for r in controls]),
            "treatment_pass_rate": _avg([1.0 if r.get("passed") else 0.0 for r in treatments]),
            "token_ratio": token_ratio,
            "time_ratio": time_ratio,
            "control_churn": _avg([v for r in controls if (v := num(r, "churn")) is not None]),
            "treatment_churn": _avg([v for r in treatments if (v := num(r, "churn")) is not None]),
            "control_unrelated_files": _avg([v for r in controls if (v := num(r, "unrelated_files")) is not None]),
            "treatment_unrelated_files": _avg([v for r in treatments if (v := num(r, "unrelated_files")) is not None]),
        })
    return {
        "schema_version": 2,
        "policy": {
            "min_pairs": min_pairs,
            "confidence": confidence,
            "bootstrap_samples": bootstrap_samples,
            "min_effect": min_effect,
            "costly_ratio": costly_ratio,
            "strong_claims_require": "minimum pairs and a bootstrap CI separated from zero by the minimum effect",
        },
        "entries": entries,
    }


def mark_freshness(registry: dict[str, Any], repo: Path) -> None:
    for entry in registry.get("entries", []):
        skill = str(entry.get("skill") or "")
        path = repo / "skills" / skill
        if not (path / "SKILL.md").is_file():
            entry["freshness"] = "missing-skill"
            continue
        current = sha256_tree(path)
        entry["current_skill_sha256"] = current
        entry["freshness"] = "current" if current == entry.get("skill_sha256") else "stale"
        if entry["freshness"] != "current":
            entry["strong_evidence"] = False


def render_markdown(registry: dict[str, Any]) -> str:
    lines = [
        "# Skill Effectiveness Registry",
        "",
        "| Provider | Model | Skill | Pairs | Classification | Strong | Score Δ | 95% CI | Win rate | Token ratio | Time ratio | Freshness |",
        "| --- | --- | --- | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for entry in registry["entries"]:
        fmt = lambda v: "n/a" if v is None else f"{v:.2f}"
        ci = entry.get("bootstrap_ci") or [None, None]
        ci_text = "n/a" if ci[0] is None else f"[{ci[0]:+.2f}, {ci[1]:+.2f}]"
        lines.append(
            f"| {entry['provider']} | {entry['model']} | {entry['skill']} | {entry['pairs']} | {entry['classification']} | "
            f"{'yes' if entry.get('strong_evidence') else 'no'} | {entry['score_delta']:+.2f} | {ci_text} | {fmt(entry.get('win_rate'))} | "
            f"{fmt(entry.get('token_ratio'))} | {fmt(entry.get('time_ratio'))} | {entry.get('freshness', 'unchecked')} |"
        )
    lines += [
        "",
        "Strong evidence is version-bound. Re-run after the skill, benchmark case, provider CLI, or model changes.",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build version-bound skill-effectiveness evidence from repeated live-eval JSONL.")
    parser.add_argument("records", nargs="+", type=Path)
    parser.add_argument("--min-pairs", type=int, default=5)
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--bootstrap-samples", type=int, default=5000)
    parser.add_argument("--min-effect", type=float, default=0.05)
    parser.add_argument("--costly-ratio", type=float, default=1.5)
    parser.add_argument("--repo", type=Path, default=None, help="Check registry skill hashes against this repository")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--strong-only", action="store_true", help="Emit only entries with strong current evidence")
    parser.add_argument("--fail-on-harmful", action="store_true")
    parser.add_argument("--fail-on-stale", action="store_true")
    args = parser.parse_args(argv)
    try:
        registry = build_registry(
            load_records(args.records), args.min_pairs, confidence=args.confidence,
            bootstrap_samples=args.bootstrap_samples, min_effect=args.min_effect, costly_ratio=args.costly_ratio,
        )
        if args.repo:
            mark_freshness(registry, args.repo.resolve())
        if args.strong_only:
            registry["entries"] = [e for e in registry["entries"] if e.get("strong_evidence") and e.get("freshness", "current") == "current"]
    except (OSError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2
    text = render_markdown(registry) if args.markdown else json.dumps(registry, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    harmful = [e for e in registry["entries"] if e["classification"] == "HARMFUL" and e.get("strong_evidence")]
    stale = [e for e in registry["entries"] if e.get("freshness") == "stale"]
    if args.fail_on_harmful and harmful:
        return 1
    if args.fail_on_stale and stale:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
