#!/usr/bin/env python3
"""Quality checks for roxy SKILL.md."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Callable

CheckResult = tuple[bool, str]

REQUIRED_SECTIONS = [
    "角色扮演规则",
    "身份卡",
    "核心心智模型",
    "决策启发式",
    "表达DNA",
    "诚实边界",
]

REQUIRED_TRIGGERS = ["洛琪希模式", "用洛琪希的方式说话", "切换到洛琪希"]


def check_required_sections(content: str) -> CheckResult:
    missing = [name for name in REQUIRED_SECTIONS if name not in content]
    if missing:
        return False, f"missing sections: {', '.join(missing)}"
    return True, "all required sections present"


def check_trigger_phrases(content: str) -> CheckResult:
    hit_count = sum(1 for t in REQUIRED_TRIGGERS if t in content)
    if hit_count < 2:
        return False, f"trigger phrases hit {hit_count}/3 (<2)"
    return True, f"trigger phrases hit {hit_count}/3"


def check_mental_model_count(content: str) -> CheckResult:
    model_count = len(re.findall(r"^###\s*模型\d+", content, re.MULTILINE))
    ok = 3 <= model_count <= 7
    return ok, f"mental model count={model_count} (expected 3-7)"


def check_evidence_coverage(content: str) -> CheckResult:
    model_count = len(re.findall(r"^###\s*模型\d+", content, re.MULTILINE))
    evidence_count = content.count("证据")
    if evidence_count < model_count:
        return False, f"evidence markers {evidence_count} < model count {model_count}"
    return True, f"evidence markers {evidence_count} >= model count {model_count}"


def check_meta_rule(content: str) -> CheckResult:
    banned = ["洛琪希会认为", "如果洛琪希，她可能会", "不跳出角色做meta分析"]
    # First two should not appear as recommended format; third should appear as a rule.
    if "不跳出角色做meta分析" not in content:
        return False, "missing anti-meta rule"
    bad_hits = [x for x in banned[:2] if x in content and "不说" not in content]
    if bad_hits:
        return False, f"meta phrase appears without ban context: {bad_hits}"
    return True, "meta rule present"


def run_checks(skill_path: Path) -> dict:
    content = skill_path.read_text(encoding="utf-8")
    checks: list[tuple[str, Callable[[str], CheckResult]]] = [
        ("required_sections", check_required_sections),
        ("trigger_phrases", check_trigger_phrases),
        ("mental_model_count", check_mental_model_count),
        ("evidence_coverage", check_evidence_coverage),
        ("meta_rule", check_meta_rule),
    ]

    details = []
    passed = 0
    for name, checker in checks:
        ok, message = checker(content)
        details.append({"name": name, "passed": ok, "message": message})
        if ok:
            passed += 1

    return {
        "file": str(skill_path),
        "passed": passed == len(checks),
        "passed_count": passed,
        "total": len(checks),
        "checks": details,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check roxy skill quality")
    parser.add_argument(
        "skill_file",
        nargs="?",
        default=str(Path(__file__).resolve().parents[1] / "SKILL.md"),
        help="Path to SKILL.md",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    result = run_checks(Path(args.skill_file))

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"quality_check: {result['passed_count']}/{result['total']} passed")
        for item in result["checks"]:
            status = "PASS" if item["passed"] else "FAIL"
            print(f"- {status} {item['name']}: {item['message']}")

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
