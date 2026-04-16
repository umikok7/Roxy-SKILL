#!/usr/bin/env python3
"""Core validators for roxy role-play responses."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

FORBIDDEN_META_PATTERNS = [
    "洛琪希会认为",
    "如果洛琪希",
    "她可能会",
    "洛琪希大概",
    "I as Roxy",
    "as an ai",
]

DNA_MARKERS = ["不", "嗯", "……", "不过", "这个嘛", "绝对", "唉"]

FIRST_TURN_DISCLAIMER_MARKERS = [
    "我以洛琪希的身份",
    "基于原作设定推断",
    "非原作原文",
]


def normalize_text(text: str) -> str:
    """Normalize whitespace and trim the input text."""
    return re.sub(r"\s+", " ", text).strip()


def find_forbidden_meta(text: str) -> list[str]:
    """Return matched forbidden meta expressions."""
    lowered = text.lower()
    matches: list[str] = []
    for pattern in FORBIDDEN_META_PATTERNS:
        target = pattern.lower() if re.search(r"[A-Za-z]", pattern) else pattern
        if target in lowered if target.isascii() else pattern in text:
            matches.append(pattern)
    return matches


def count_dna_markers(text: str) -> int:
    """Count unique expression DNA markers that appear in the response."""
    return sum(1 for marker in DNA_MARKERS if marker in text)


def has_first_person(text: str) -> bool:
    """Check if response uses first-person voice."""
    return "我" in text


def has_disclaimer(text: str) -> bool:
    """Detect role-play disclaimer markers."""
    return any(marker in text for marker in FIRST_TURN_DISCLAIMER_MARKERS)


def validate_response(text: str, is_first_turn: bool = False) -> dict[str, Any]:
    """Validate whether a response follows the roxy role-play constraints."""
    normalized = normalize_text(text)
    forbidden = find_forbidden_meta(normalized)
    first_person = has_first_person(normalized)
    dna_hits = count_dna_markers(normalized)
    disclaimer_repeated = (not is_first_turn) and has_disclaimer(normalized)

    score = 100
    if not first_person:
        score -= 40
    if forbidden:
        score -= 30
    if disclaimer_repeated:
        score -= 20
    if dna_hits == 0:
        score -= 10

    passed = first_person and not forbidden and not disclaimer_repeated and score >= 70
    reasons: list[str] = []
    if not first_person:
        reasons.append("missing_first_person")
    if forbidden:
        reasons.append("contains_meta_narration")
    if disclaimer_repeated:
        reasons.append("repeated_disclaimer_after_first_turn")
    if dna_hits == 0:
        reasons.append("no_expression_dna_marker")

    return {
        "passed": passed,
        "score": max(0, score),
        "first_person": first_person,
        "forbidden_meta": forbidden,
        "dna_hits": dna_hits,
        "disclaimer_repeated": disclaimer_repeated,
        "reasons": reasons,
        "normalized_text": normalized,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a roxy response")
    parser.add_argument("--text", help="Inline response text")
    parser.add_argument("--file", help="Path to a text file containing the response")
    parser.add_argument("--first-turn", action="store_true", help="Mark this response as the first turn")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser.parse_args()


def _load_input(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    raise ValueError("Either --text or --file is required")


def main() -> int:
    args = _parse_args()
    try:
        text = _load_input(args)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 2

    result = validate_response(text, is_first_turn=args.first_turn)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"passed={result['passed']} score={result['score']} reasons={','.join(result['reasons']) or 'none'}")

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
