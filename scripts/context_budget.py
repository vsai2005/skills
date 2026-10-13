#!/usr/bin/env python3
"""Measure discovery, core-skill, and progressive-disclosure context budgets."""
from __future__ import annotations

import argparse, json, math, re, sys
from dataclasses import asdict, dataclass
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
RESOURCE_DIRS = ("references", "assets", "scripts")
COMPARISON_FIELDS = (
    "total_discovery_chars",
    "rough_discovery_tokens",
    "rough_total_skill_tokens",
    "rough_total_resource_tokens",
    "total_resource_bytes",
    "max_skill_tokens",
    "max_initial_load_tokens",
)


@dataclass(frozen=True)
class SkillBudget:
    name: str
    description_chars: int
    discovery_chars: int
    skill_lines: int
    skill_bytes: int
    rough_skill_tokens: int
    resource_files: int
    resource_bytes: int
    rough_resource_tokens: int
    largest_resource_path: str | None
    largest_resource_bytes: int
    rough_largest_resource_tokens: int


def _frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"malformed frontmatter: {path}")
    data: dict[str, str] = {}
    for raw in match.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#") or ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        value = value.strip()
        if value.startswith(("'", '"')) and len(value) >= 2 and value.endswith(value[0]):
            value = value[1:-1]
        data[key.strip()] = value
    return data


def _resources(skill_dir: Path) -> tuple[int, int, int, str | None, int, int]:
    files: list[Path] = []
    for folder in RESOURCE_DIRS:
        path = skill_dir / folder
        if path.is_dir():
            files.extend(
                item
                for item in path.rglob("*")
                if item.is_file()
                and "__pycache__" not in item.parts
                and item.suffix.lower() not in {".pyc", ".pyo"}
            )

    total_bytes = 0
    total_chars = 0
    largest_path: str | None = None
    largest_bytes = 0
    largest_tokens = 0

    for path in files:
        data = path.read_bytes()
        total_bytes += len(data)
        try:
            chars = len(data.decode("utf-8"))
        except UnicodeDecodeError:
            chars = len(data)
        total_chars += chars

        tokens = math.ceil(chars / 4)
        if tokens > largest_tokens or (tokens == largest_tokens and len(data) > largest_bytes):
            largest_path = path.relative_to(skill_dir).as_posix()
            largest_bytes = len(data)
            largest_tokens = tokens

    return (
        len(files),
        total_bytes,
        math.ceil(total_chars / 4),
        largest_path,
        largest_bytes,
        largest_tokens,
    )


def measure(root: Path) -> list[SkillBudget]:
    skills_root = root / "skills"
    if not skills_root.is_dir():
        raise ValueError(f"skills directory missing: {skills_root}")

    budgets: list[SkillBudget] = []
    for skill_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue

        text = skill_md.read_text(encoding="utf-8")
        meta = _frontmatter(skill_md)
        name = meta.get("name", skill_dir.name)
        description = meta.get("description", "")
        (
            resource_files,
            resource_bytes,
            resource_tokens,
            largest_resource_path,
            largest_resource_bytes,
            largest_resource_tokens,
        ) = _resources(skill_dir)

        budgets.append(
            SkillBudget(
                name=name,
                description_chars=len(description),
                discovery_chars=len(name) + len(description),
                skill_lines=len(text.splitlines()),
                skill_bytes=len(text.encode()),
                rough_skill_tokens=math.ceil(len(text) / 4),
                resource_files=resource_files,
                resource_bytes=resource_bytes,
                rough_resource_tokens=resource_tokens,
                largest_resource_path=largest_resource_path,
                largest_resource_bytes=largest_resource_bytes,
                rough_largest_resource_tokens=largest_resource_tokens,
            )
        )
    return budgets


def summarize(budgets: list[SkillBudget]) -> dict[str, int]:
    total_discovery_chars = sum(item.discovery_chars for item in budgets)
    rough_discovery_tokens = math.ceil(total_discovery_chars / 4)
    max_skill_tokens = max((item.rough_skill_tokens for item in budgets), default=0)
    return {
        "skills": len(budgets),
        "total_discovery_chars": total_discovery_chars,
        "rough_discovery_tokens": rough_discovery_tokens,
        "rough_total_skill_tokens": sum(item.rough_skill_tokens for item in budgets),
        "rough_total_resource_tokens": sum(item.rough_resource_tokens for item in budgets),
        "total_resource_bytes": sum(item.resource_bytes for item in budgets),
        "max_description_chars": max((item.description_chars for item in budgets), default=0),
        "max_skill_lines": max((item.skill_lines for item in budgets), default=0),
        "max_skill_tokens": max_skill_tokens,
        "max_resource_bytes": max((item.resource_bytes for item in budgets), default=0),
        "max_single_resource_tokens": max(
            (item.rough_largest_resource_tokens for item in budgets), default=0
        ),
        "max_initial_load_tokens": rough_discovery_tokens + max_skill_tokens,
    }


def violations(
    budgets: list[SkillBudget],
    *,
    max_total_discovery_chars: int,
    max_description_chars: int,
    max_skill_lines: int,
    max_skill_tokens: int,
    max_resource_bytes: int,
    max_total_resource_bytes: int,
) -> list[str]:
    problems: list[str] = []
    stats = summarize(budgets)

    if stats["total_discovery_chars"] > max_total_discovery_chars:
        problems.append(
            f"total discovery metadata is {stats['total_discovery_chars']} chars; "
            f"budget is {max_total_discovery_chars}"
        )
    if stats["total_resource_bytes"] > max_total_resource_bytes:
        problems.append(
            f"total progressive-disclosure resources are {stats['total_resource_bytes']} bytes; "
            f"budget is {max_total_resource_bytes}"
        )

    for item in budgets:
        if item.description_chars > max_description_chars:
            problems.append(
                f"{item.name} description is {item.description_chars} chars; "
                f"budget is {max_description_chars}"
            )
        if item.skill_lines > max_skill_lines:
            problems.append(
                f"{item.name}/SKILL.md is {item.skill_lines} lines; budget is {max_skill_lines}"
            )
        if item.rough_skill_tokens > max_skill_tokens:
            problems.append(
                f"{item.name}/SKILL.md is ~{item.rough_skill_tokens} tokens; "
                f"hard budget is {max_skill_tokens}"
            )
        if item.resource_bytes > max_resource_bytes:
            problems.append(
                f"{item.name} resources are {item.resource_bytes} bytes; "
                f"budget is {max_resource_bytes}"
            )
    return problems


def budget_warnings(
    budgets: list[SkillBudget],
    *,
    max_total_discovery_chars: int,
    warn_discovery_percent: int,
    soft_skill_tokens: int,
    warn_reference_tokens: int,
    warn_initial_load_tokens: int,
) -> list[str]:
    warnings: list[str] = []
    stats = summarize(budgets)

    if max_total_discovery_chars > 0:
        utilization = stats["total_discovery_chars"] * 100 / max_total_discovery_chars
        if utilization >= warn_discovery_percent:
            warnings.append(
                f"discovery metadata uses {utilization:.1f}% of its hard budget "
                f"({stats['total_discovery_chars']}/{max_total_discovery_chars} chars)"
            )

    for item in budgets:
        if item.rough_skill_tokens > soft_skill_tokens:
            warnings.append(
                f"{item.name}/SKILL.md is ~{item.rough_skill_tokens} tokens; "
                f"soft target is {soft_skill_tokens}"
            )
        if item.rough_largest_resource_tokens > warn_reference_tokens:
            warnings.append(
                f"{item.name}/{item.largest_resource_path} is "
                f"~{item.rough_largest_resource_tokens} tokens; "
                f"large progressive-resource warning is {warn_reference_tokens}"
            )

        initial_tokens = stats["rough_discovery_tokens"] + item.rough_skill_tokens
        if initial_tokens > warn_initial_load_tokens:
            warnings.append(
                f"{item.name} discovery + root initial load is ~{initial_tokens} tokens; "
                f"guidance target is {warn_initial_load_tokens} before references"
            )

    return warnings


def compare_summaries(current: dict[str, int], baseline: dict[str, object]) -> dict[str, int]:
    deltas: dict[str, int] = {}
    for field in COMPARISON_FIELDS:
        before = baseline.get(field)
        after = current.get(field)
        if isinstance(before, int) and isinstance(after, int):
            deltas[field] = after - before
    return deltas


def _load_comparison(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read comparison JSON {path}: {exc}") from exc

    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise ValueError(f"comparison JSON has no summary object: {path}")
    return summary


def _signed(value: int) -> str:
    return f"{value:+d}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Measure skill discovery/core/resource context budgets."
    )
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--max-total-discovery-chars", type=int, default=4500)
    parser.add_argument("--max-description-chars", type=int, default=320)
    parser.add_argument("--max-skill-lines", type=int, default=500)
    parser.add_argument("--soft-skill-tokens", type=int, default=1800)
    parser.add_argument("--max-skill-tokens", type=int, default=2500)
    parser.add_argument("--max-resource-bytes", type=int, default=50000)
    parser.add_argument("--max-total-resource-bytes", type=int, default=300000)
    parser.add_argument("--warn-discovery-percent", type=int, default=85)
    parser.add_argument("--warn-reference-tokens", type=int, default=5000)
    parser.add_argument("--warn-initial-load-tokens", type=int, default=3000)
    parser.add_argument(
        "--compare-json",
        type=Path,
        help="Compare the current summary with a prior --json output.",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on-budget", action="store_true")
    args = parser.parse_args(argv)

    try:
        budgets = measure(args.root.resolve())
        baseline = _load_comparison(args.compare_json) if args.compare_json else None
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    problems = violations(
        budgets,
        max_total_discovery_chars=args.max_total_discovery_chars,
        max_description_chars=args.max_description_chars,
        max_skill_lines=args.max_skill_lines,
        max_skill_tokens=args.max_skill_tokens,
        max_resource_bytes=args.max_resource_bytes,
        max_total_resource_bytes=args.max_total_resource_bytes,
    )
    warnings = budget_warnings(
        budgets,
        max_total_discovery_chars=args.max_total_discovery_chars,
        warn_discovery_percent=args.warn_discovery_percent,
        soft_skill_tokens=args.soft_skill_tokens,
        warn_reference_tokens=args.warn_reference_tokens,
        warn_initial_load_tokens=args.warn_initial_load_tokens,
    )
    summary = summarize(budgets)
    comparison = compare_summaries(summary, baseline) if baseline else None

    if args.json:
        payload: dict[str, object] = {
            "summary": summary,
            "skills": [asdict(item) for item in budgets],
            "warnings": warnings,
            "violations": problems,
        }
        if comparison is not None:
            payload["comparison"] = comparison
        print(json.dumps(payload, indent=2))
    else:
        print(f"Skills: {summary['skills']}")
        print(
            f"Discovery metadata: {summary['total_discovery_chars']} chars "
            f"(~{summary['rough_discovery_tokens']} tokens)"
        )
        print(
            "Approximate SKILL.md total: "
            f"{summary['rough_total_skill_tokens']} tokens "
            "(all skills; normally selective)"
        )
        print(
            "Progressive-disclosure resources: "
            f"{summary['total_resource_bytes']} bytes "
            f"(~{summary['rough_total_resource_tokens']} tokens, conditionally loaded)"
        )
        print(
            "Largest selected-skill initial load: "
            f"~{summary['max_initial_load_tokens']} tokens "
            "(discovery + one root; excludes repository/host instructions and references)"
        )
        for item in budgets:
            largest = (
                f", largest {item.largest_resource_path} "
                f"~{item.rough_largest_resource_tokens} tokens"
                if item.largest_resource_path
                else ""
            )
            print(
                f"- {item.name}: description {item.description_chars} chars, "
                f"SKILL.md {item.skill_lines} lines (~{item.rough_skill_tokens} tokens), "
                f"resources {item.resource_files} files/{item.resource_bytes} bytes{largest}"
            )

        if warnings:
            print("Budget warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        else:
            print("Budget warnings: none")

        if problems:
            print("Budget violations:")
            for problem in problems:
                print(f"  - {problem}")
        else:
            print("Budget violations: none")

        if comparison is not None:
            print(f"Comparison vs {args.compare_json}:")
            for field in COMPARISON_FIELDS:
                if field in comparison:
                    print(f"  - {field}: {_signed(comparison[field])}")

    return 1 if args.fail_on_budget and problems else 0


if __name__ == "__main__":
    sys.exit(main())
