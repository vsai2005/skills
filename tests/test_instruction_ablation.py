import json
from pathlib import Path
import tempfile
import unittest

from scripts.instruction_ablation import compare, remove_section


def write_records(tmp: str, rows: list[dict]) -> Path:
    path = Path(tmp) / "records.jsonl"
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )
    return path


def row(
    variant: str,
    *,
    score: float = 1.0,
    tokens: tuple[int, int] | None = (700, 300),
    duration: float = 10.0,
    tool_events: int = 10,
    protected: bool = False,
) -> dict:
    item = {
        "variant": variant,
        "status": "completed",
        "score_fraction": score,
        "passed": score >= 0.8,
        "duration_seconds": duration,
        "workflow_metrics": {"tool_event_count": tool_events},
    }
    if tokens is not None:
        item["usage"] = {
            "input_tokens": tokens[0],
            "output_tokens": tokens[1],
        }
    if protected:
        item["protected_instruction"] = True
    return item


class AblationTests(unittest.TestCase):
    def test_remove_named_section_only(self):
        text = "# X\n\n## A\none\n\n### A1\ntwo\n\n## B\nthree\n"
        out = remove_section(text, "A")
        self.assertNotIn("one", out)
        self.assertNotIn("A1", out)
        self.assertIn("## B", out)

    def test_numbered_heading_can_be_named_without_number(self):
        text = "# X\n\n## 2. Investigate cause\nbody\n\n## 3. Verify\nkeep\n"
        out = remove_section(text, "Investigate cause")
        self.assertNotIn("body", out)
        self.assertIn("## 3. Verify", out)

    def test_prune_candidate_requires_quality_and_material_token_savings(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_records(
                tmp,
                [
                    row("control", score=0.7, tokens=(600, 300)),
                    row("full", score=1.0, tokens=(700, 300), duration=10, tool_events=10),
                    row("ablated", score=0.995, tokens=(550, 250), duration=9, tool_events=9),
                ],
            )
            result = compare(path)
            self.assertEqual("PRUNE_CANDIDATE", result["decision"])
            self.assertEqual(0.8, result["deltas"]["token_ratio"])
            self.assertEqual(0.2, result["deltas"]["token_savings_fraction"])
            self.assertTrue(result["checks"]["quality_non_inferior"])

    def test_quality_regression_keeps_section_even_when_tokens_drop(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_records(
                tmp,
                [
                    row("full", score=1.0, tokens=(700, 300)),
                    row("ablated", score=0.9, tokens=(400, 200)),
                ],
            )
            result = compare(path)
            self.assertEqual("KEEP_SECTION", result["decision"])
            self.assertFalse(result["checks"]["quality_non_inferior"])

    def test_missing_token_data_is_not_a_prune_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_records(
                tmp,
                [
                    row("full", score=1.0, tokens=None),
                    row("ablated", score=1.0, tokens=None),
                ],
            )
            result = compare(path)
            self.assertEqual("INSUFFICIENT_TOKEN_DATA", result["decision"])
            self.assertFalse(result["checks"]["token_data_available"])

    def test_small_token_change_is_not_material_savings(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_records(
                tmp,
                [
                    row("full", tokens=(700, 300)),
                    row("ablated", tokens=(690, 300)),
                ],
            )
            result = compare(path)
            self.assertEqual("NO_MATERIAL_TOKEN_SAVINGS", result["decision"])
            self.assertFalse(result["checks"]["token_savings_meets_threshold"])

    def test_material_runtime_regression_vetoes_token_savings(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_records(
                tmp,
                [
                    row("full", tokens=(700, 300), duration=10, tool_events=10),
                    row("ablated", tokens=(500, 250), duration=12, tool_events=10),
                ],
            )
            result = compare(path)
            self.assertEqual("COST_REGRESSION_KEEP", result["decision"])
            self.assertTrue(result["checks"]["time_regressed_materially"])

    def test_explicit_protected_flag_never_returns_prune_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_records(
                tmp,
                [
                    row("full", tokens=(700, 300)),
                    row("ablated", tokens=(400, 200)),
                ],
            )
            result = compare(path, protected=True)
            self.assertEqual("PROTECTED_KEEP", result["decision"])
            self.assertTrue(result["checks"]["protected"])

    def test_record_can_mark_instruction_protected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_records(
                tmp,
                [
                    row("full", tokens=(700, 300), protected=True),
                    row("ablated", tokens=(400, 200), protected=True),
                ],
            )
            result = compare(path)
            self.assertEqual("PROTECTED_KEEP", result["decision"])


if __name__ == "__main__":
    unittest.main()
