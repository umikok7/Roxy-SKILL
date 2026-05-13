# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Roxy Skill is a character role-play skill for Claude Code, modeling Roxy Migurdia (水聖級魔术师) from the light novel "Mushoku Tensei". It provides a distillation of her speech patterns, decision-making heuristics, and cognitive models derived from 172 dialogue records across 6 life periods.

## Development Commands

### Quality Checks
```bash
python scripts/quality_check.py SKILL.md --json
python3 scripts/quality_check.py SKILL.md --json
```

### Regression Tests
```bash
python scripts/regression_test.py --json
python3 scripts/regression_test.py --json
```

### Unit Tests
```bash
python -m unittest discover tests -v
python3 -m unittest discover tests -v
```

## Architecture

### Core Scripts
- **scripts/core.py** - Response validator: checks first-person voice, forbidden meta patterns, DNA markers, disclaimer repetition, and computes a score (0-100).
- **scripts/quality_check.py** - SKILL.md structural validator: ensures required sections, trigger phrases, mental model count (3-7), evidence coverage, and anti-meta rules.
- **scripts/regression_test.py** - Runs regression cases against `core.py`'s `validate_response()`.

### References (references/research/)
The research layer follows a three-tier trigger system to avoid "have data but not recall" drift:
- **06-timeline.md** - Life periods and chronology (check first to avoid era mismatches)
- **05-decisions.md** - Key decisions and value orientations
- **02-conversations.md** + **03-expression-dna.md** - Dialogue patterns and speech DNA (default lightweight read)
- **04-external-views.md** - Controversial/conflicting perspectives

### Activation Triggers
Skill activates when user says: "洛琪希模式", "用洛琪希的方式说话", or "切换到洛琪希"

### Research Read Order (Full)
06 → 05 → 02 → 03 → 04

## Key Constraints

- First-person only: use 「我」 not 「洛琪希会认为...」
- Disclaimer only on first activation, never repeated
- No meta-commentary跳出角色
- DNA markers must appear: 「不」, 「嗯」, 「……」, 「不过」, 「这个嘛」, 「绝对」
