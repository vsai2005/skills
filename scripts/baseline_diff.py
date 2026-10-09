#!/usr/bin/env python3
"""Compare failure inventories from a baseline and candidate run.

A failure is only called pre-existing when its stable identity and available
failure signature agree. Same test ID with a changed signature is conservatively
classified as a regression so new failures are not hidden behind an old red test.

Supported inputs:
- text: ``id<TAB>signature<TAB>detail`` (signature/detail are optional)
- JSON list: strings or objects with id/key/name plus signature/detail/message
- JUnit XML: failing/error testcases are converted into stable IDs + signatures
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


@dataclass(frozen=True)
class FailureRecord:
    key: str
    signature: str = ""
    detail: str = ""


@dataclass(frozen=True)
class ClassifiedFailure:
    key: str
    signature: str
    detail: str
    classification: str
    reason: str


def normalize_signature(value: str) -> str:
    value = ANSI_RE.sub("", value).replace("\r\n", "\n").replace("\r", "\n")
    return " ".join(value.split())


def _unique(records: Iterable[FailureRecord], source: Path) -> list[FailureRecord]:
    result: list[FailureRecord] = []
    seen: set[str] = set()
    for record in records:
        if record.key in seen:
            raise ValueError(f"duplicate failure id {record.key!r} in {source}")
        seen.add(record.key)
        result.append(record)
    return result


def _valid_key(raw_key: object, index: int, source: Path) -> str:
    if raw_key is None:
        raise ValueError(f"null failure id at index {index} in {source}")
    if not isinstance(raw_key, (str, int, float)) or isinstance(raw_key, bool):
        raise ValueError(f"invalid failure id at index {index} in {source}")
    key = str(raw_key).strip()
    if not key:
        raise ValueError(f"empty failure id at index {index} in {source}")
    return key


def _from_json(data: object, source: Path) -> list[FailureRecord]:
    if not isinstance(data, list):
        raise ValueError(f"JSON failure inventory must be a list: {source}")
    records: list[FailureRecord] = []
    for index, item in enumerate(data):
        if isinstance(item, str):
            key = item.strip()
            if not key:
                raise ValueError(f"empty failure id at index {index} in {source}")
            signature = ""
            detail = ""
        elif isinstance(item, dict):
            if "id" in item:
                raw_key = item["id"]
            elif "key" in item:
                raw_key = item["key"]
            elif "name" in item:
                raw_key = item["name"]
            else:
                raise ValueError(f"missing failure id at index {index} in {source}")
            key = _valid_key(raw_key, index, source)
            detail = str(item.get("detail", item.get("message", ""))).strip()
            raw_signature = item.get("signature")
            signature = normalize_signature(str(raw_signature if raw_signature is not None else detail))
        else:
            raise ValueError(f"unsupported JSON item at index {index} in {source}")
        records.append(FailureRecord(key=key, signature=signature, detail=detail))
    return _unique(records, source)


def _from_text(text: str, source: Path) -> list[FailureRecord]:
    records: list[FailureRecord] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = raw.split("\t", 2)
        key = parts[0].strip()
        if not key:
            raise ValueError(f"empty failure id at line {lineno} in {source}")
        signature = normalize_signature(parts[1]) if len(parts) >= 2 else ""
        detail = parts[2].strip() if len(parts) >= 3 else (parts[1].strip() if len(parts) == 2 else "")
        records.append(FailureRecord(key=key, signature=signature, detail=detail))
    return _unique(records, source)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _junit_identity(testcase: ET.Element, parent_map: dict[ET.Element, ET.Element]) -> str:
    name = (testcase.attrib.get("name") or "").strip()
    classname = (testcase.attrib.get("classname") or testcase.attrib.get("class") or "").strip()
    if not name:
        return ""

    file_name = (testcase.attrib.get("file") or "").strip()
    package = (testcase.attrib.get("package") or "").strip()
    suite_name = ""
    suite_package = ""
    parent = parent_map.get(testcase)
    while parent is not None:
        if _local_name(parent.tag) == "testsuite":
            if not suite_name:
                suite_name = (parent.attrib.get("name") or "").strip()
            if not suite_package:
                suite_package = (parent.attrib.get("package") or "").strip()
        parent = parent_map.get(parent)

    prefix = file_name or package or suite_package or suite_name
    pieces = [part for part in (prefix, classname, name) if part]
    # Avoid noisy repetition such as package == classname while preserving the
    # most specific path/suite discriminator available.
    deduped: list[str] = []
    for part in pieces:
        if not deduped or deduped[-1] != part:
            deduped.append(part)
    return "::".join(deduped)


def _from_junit_xml(text: str, source: Path) -> list[FailureRecord]:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise ValueError(f"invalid JUnit XML in {source}: {exc}") from exc
    parent_map = {child: parent for parent in root.iter() for child in parent}
    records: list[FailureRecord] = []
    for testcase in root.iter():
        if _local_name(testcase.tag) != "testcase":
            continue
        failure_node = next(
            (child for child in testcase if _local_name(child.tag) in {"failure", "error"}),
            None,
        )
        if failure_node is None:
            continue
        key = _junit_identity(testcase, parent_map)
        if not key:
            raise ValueError(f"JUnit testcase without name in {source}")
        message = (failure_node.attrib.get("message") or "").strip()
        body = (failure_node.text or "").strip()
        signature = normalize_signature("\n".join(part for part in (message, body) if part))
        detail = message or normalize_signature(body)[:500]
        records.append(FailureRecord(key=key, signature=signature, detail=detail))
    return _unique(records, source)


def load_failures(path: Path) -> list[FailureRecord]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    suffix = path.suffix.lower()
    if suffix == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON in {path}: {exc}") from exc
        return _from_json(data, path)
    if suffix == ".xml":
        return _from_junit_xml(text, path)
    return _from_text(text, path)


def compare_failures(
    baseline: list[FailureRecord], current: list[FailureRecord]
) -> tuple[list[ClassifiedFailure], list[FailureRecord]]:
    baseline_by_key = {record.key: record for record in baseline}
    current_keys = {record.key for record in current}
    classified: list[ClassifiedFailure] = []
    for record in current:
        previous = baseline_by_key.get(record.key)
        if previous is None:
            classification = "regression"
            reason = "new-failure-id"
        elif previous.signature and record.signature and previous.signature == record.signature:
            classification = "pre-existing"
            reason = "same-id-and-signature"
        elif not previous.signature and not record.signature:
            classification = "pre-existing"
            reason = "same-id-no-signature-available"
        elif previous.signature != record.signature:
            classification = "regression"
            reason = "same-id-signature-changed"
        else:
            classification = "regression"
            reason = "signature-equivalence-unproven"
        classified.append(
            ClassifiedFailure(
                key=record.key,
                signature=record.signature,
                detail=record.detail,
                classification=classification,
                reason=reason,
            )
        )
    resolved = [record for record in baseline if record.key not in current_keys]
    return classified, resolved


def summary(classified: list[ClassifiedFailure], resolved: list[FailureRecord]) -> dict[str, object]:
    pre_existing = sum(item.classification == "pre-existing" for item in classified)
    regressions = sum(item.classification == "regression" for item in classified)
    changed_signatures = sum(item.reason == "same-id-signature-changed" for item in classified)
    return {
        "current_failures": len(classified),
        "pre_existing": pre_existing,
        "regressions": regressions,
        "changed_signature_regressions": changed_signatures,
        "resolved_from_baseline": len(resolved),
    }


def render_text(classified: list[ClassifiedFailure], resolved: list[FailureRecord]) -> str:
    stats = summary(classified, resolved)
    lines = [
        f"Current failures: {stats['current_failures']}",
        f"Pre-existing: {stats['pre_existing']}",
        f"Regressions: {stats['regressions']}",
        f"Changed-signature regressions: {stats['changed_signature_regressions']}",
        f"Resolved from baseline: {stats['resolved_from_baseline']}",
        "",
        "Failure classification:",
    ]
    if classified:
        for item in classified:
            detail = f" — {item.detail}" if item.detail else ""
            lines.append(f"- [{item.classification}] {item.key} ({item.reason}){detail}")
    else:
        lines.append("- none")
    if resolved:
        lines.extend(["", "Baseline failures no longer present:"])
        for item in resolved:
            lines.append(f"- {item.key}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify current failures against a baseline failure inventory.")
    parser.add_argument("baseline", type=Path, help="Baseline inventory (.txt/.json/.xml)")
    parser.add_argument("current", type=Path, help="Current inventory (.txt/.json/.xml)")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--fail-on-regression", action="store_true", help="Exit 1 when any regression is present")
    args = parser.parse_args(argv)

    try:
        baseline = load_failures(args.baseline)
        current = load_failures(args.current)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    classified, resolved = compare_failures(baseline, current)
    stats = summary(classified, resolved)
    if args.json:
        print(json.dumps({
            "summary": stats,
            "failures": [asdict(item) for item in classified],
            "resolved_from_baseline": [asdict(item) for item in resolved],
        }, indent=2))
    else:
        print(render_text(classified, resolved))

    return 1 if args.fail_on_regression and stats["regressions"] else 0


if __name__ == "__main__":
    sys.exit(main())
