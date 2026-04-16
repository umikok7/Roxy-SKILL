#!/usr/bin/env python3
"""Run a small regression set against roxy response validator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core import validate_response


def run_regression(cases_path: Path) -> dict:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))

    failures = []
    results = []
    for case in cases:
        name = case["name"]
        response = case["response"]
        is_first_turn = case.get("is_first_turn", False)
        expect_pass = case["expect_pass"]
        min_score = case.get("min_score")

        outcome = validate_response(response, is_first_turn=is_first_turn)
        case_ok = outcome["passed"] == expect_pass

        if min_score is not None and outcome["score"] < min_score:
            case_ok = False

        results.append({
            "name": name,
            "expected_pass": expect_pass,
            "actual_pass": outcome["passed"],
            "score": outcome["score"],
            "reasons": outcome["reasons"],
            "ok": case_ok,
        })

        if not case_ok:
            failures.append(name)

    return {
        "cases": len(cases),
        "failed": len(failures),
        "passed": len(cases) - len(failures),
        "failures": failures,
        "results": results,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run regression checks for roxy response validator")
    parser.add_argument(
        "--cases",
        default=str(Path(__file__).resolve().parents[1] / "tests" / "regression_cases.json"),
        help="Path to regression case JSON file",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    report = run_regression(Path(args.cases))

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"regression: {report['passed']}/{report['cases']} passed")
        for item in report["results"]:
            status = "PASS" if item["ok"] else "FAIL"
            print(f"- {status} {item['name']}: score={item['score']} pass={item['actual_pass']} reasons={','.join(item['reasons']) or 'none'}")

    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
