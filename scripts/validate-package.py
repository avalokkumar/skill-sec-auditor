#!/usr/bin/env python3
"""Check Skill Security Auditor's package files without external dependencies."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def read_package_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise SystemExit(f"Cannot read {path.relative_to(ROOT)}: {error}")


SKILL_PATH = ROOT / "SKILL.md"
CHECKLIST_PATH = ROOT / "audit-checklist.md"
SKILL = read_package_file(SKILL_PATH)
CHECKLIST = read_package_file(CHECKLIST_PATH)
try:
    PLUGIN = json.loads(read_package_file(ROOT / ".claude-plugin" / "plugin.json"))
except json.JSONDecodeError as error:
    raise SystemExit(f"Fix the JSON in .claude-plugin/plugin.json: {error}")
try:
    MARKETPLACE = json.loads(read_package_file(ROOT / ".claude-plugin" / "marketplace.json"))
except json.JSONDecodeError as error:
    raise SystemExit(f"Fix the JSON in .claude-plugin/marketplace.json: {error}")


def require_match(match: re.Match[str] | None, message: str) -> re.Match[str]:
    if match is None:
        raise SystemExit(message)
    return match


# SKILL.md frontmatter: only name and description are supported fields.
frontmatter = require_match(
    re.match(r"\A---\n(.*?)\n---\n", SKILL, re.DOTALL),
    "SKILL.md must begin with YAML metadata",
).group(1)

allowed_fields = {"name", "description"}
found_fields = set(re.findall(r"(?m)^([a-zA-Z0-9_-]+):", frontmatter))
extra_fields = found_fields - allowed_fields
if extra_fields:
    raise SystemExit(f"SKILL.md frontmatter supports only name/description, found: {sorted(extra_fields)}")
if found_fields != allowed_fields:
    raise SystemExit(f"SKILL.md frontmatter must define name and description, found: {sorted(found_fields)}")

skill_name = require_match(
    re.search(r"(?m)^name:\s*(\S+)\s*$", frontmatter),
    "SKILL.md frontmatter must set name",
).group(1)
if skill_name != "auditing-skill-files":
    raise SystemExit(
        f"SKILL.md name must stay 'auditing-skill-files' to match the deployed global skill, found: {skill_name}"
    )

if len(frontmatter) > 1024:
    raise SystemExit("SKILL.md frontmatter must stay within 1024 characters")

# SKILL.md must reference the checklist file it depends on.
if "audit-checklist.md" not in SKILL:
    raise SystemExit("SKILL.md must reference audit-checklist.md")

# The three verdicts must appear, exactly as named, and nowhere renamed.
for verdict in ("SAFE", "UNSAFE", "NEEDS REVIEW"):
    if verdict not in CHECKLIST:
        raise SystemExit(f"audit-checklist.md must define the verdict: {verdict}")

# Categories in audit-checklist.md must be numbered from 1 upward without gaps.
category_numbers = [int(n) for n in re.findall(r"(?m)^## ([0-9]+)\. ", CHECKLIST)]
if category_numbers != list(range(1, len(category_numbers) + 1)):
    raise SystemExit(f"Number audit-checklist.md categories from 1 upward without gaps: {category_numbers}")

# Plugin/marketplace packaging must point at the repo root and agree on name.
if PLUGIN.get("skills") != ["./"]:
    raise SystemExit("Point the Claude plugin skill loader at the repo root")

plugin_name = PLUGIN.get("name")
marketplace_plugin_names = [p.get("name") for p in MARKETPLACE.get("plugins", [])]
if plugin_name not in marketplace_plugin_names:
    raise SystemExit(
        f"marketplace.json must list a plugin named '{plugin_name}' to match plugin.json"
    )

# Exactly one SKILL.md and one audit-checklist.md at the repo root, no stray copies/symlinks.
skill_files = {p.relative_to(ROOT) for p in ROOT.rglob("SKILL.md")}
if SKILL_PATH.is_symlink() or skill_files != {Path("SKILL.md")}:
    raise SystemExit("Keep one regular SKILL.md at the repo root")
checklist_files = {p.relative_to(ROOT) for p in ROOT.rglob("audit-checklist.md")}
if CHECKLIST_PATH.is_symlink() or checklist_files != {Path("audit-checklist.md")}:
    raise SystemExit("Keep one regular audit-checklist.md at the repo root")

print(f"Skill Security Auditor package ({plugin_name}) is valid: {len(category_numbers)} audit categories")
