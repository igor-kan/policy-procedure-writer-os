from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class BuildResult:
    output_dir: Path
    policy_count: int
    sop_count: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build policy and SOP document packs")
    parser.add_argument("--brief", required=True, help="YAML brief input path")
    parser.add_argument("--out", default="out", help="Output directory")
    return parser.parse_args()


def _validate_brief(brief: dict) -> None:
    required = ["organization", "policies", "procedures"]
    missing = [k for k in required if k not in brief]
    if missing:
        raise ValueError(f"Brief missing required keys: {missing}")
    if not isinstance(brief["policies"], list) or not brief["policies"]:
        raise ValueError("`policies` must be a non-empty list")
    if not isinstance(brief["procedures"], list) or not brief["procedures"]:
        raise ValueError("`procedures` must be a non-empty list")


def _slug(text: str) -> str:
    return "-".join(text.lower().replace("&", "and").split())


def _policy_doc(organization: str, policy: dict) -> str:
    title = str(policy.get("title", "Untitled Policy")).strip()
    purpose = str(policy.get("purpose", "")).strip()
    scope = str(policy.get("scope", "")).strip()
    controls = policy.get("controls", [])

    lines = [
        f"# {title}",
        "",
        f"Organization: {organization}",
        "",
        "## Purpose",
        purpose or "TBD",
        "",
        "## Scope",
        scope or "TBD",
        "",
        "## Controls",
    ]
    for c in controls:
        lines.append(f"- {c}")
    if not controls:
        lines.append("- TBD")

    lines.extend(
        [
            "",
            "## Review Cycle",
            "- Owner: Compliance Lead",
            "- Review frequency: quarterly",
            "- Change log required: yes",
        ]
    )
    return "\n".join(lines)


def _procedure_doc(organization: str, procedure: dict) -> tuple[str, list[dict[str, str]]]:
    title = str(procedure.get("title", "Untitled Procedure")).strip()
    trigger = str(procedure.get("trigger", "")).strip()
    steps = procedure.get("steps", [])

    lines = [
        f"# SOP - {title}",
        "",
        f"Organization: {organization}",
        "",
        "## Trigger",
        trigger or "TBD",
        "",
        "## Steps",
    ]

    checklist_rows: list[dict[str, str]] = []
    for idx, step in enumerate(steps, start=1):
        text = str(step).strip()
        lines.append(f"{idx}. {text}")
        checklist_rows.append({"procedure": title, "step_number": str(idx), "step": text, "owner": "TBD"})

    if not steps:
        lines.append("1. TBD")
        checklist_rows.append({"procedure": title, "step_number": "1", "step": "TBD", "owner": "TBD"})

    lines.extend(
        [
            "",
            "## QA and Evidence",
            "- Required evidence artifacts captured",
            "- Exception handling documented",
        ]
    )
    return "\n".join(lines), checklist_rows


def build_pack(brief_path: Path, out_root: Path) -> BuildResult:
    if not brief_path.exists():
        raise FileNotFoundError(f"Brief not found: {brief_path}")

    brief = yaml.safe_load(brief_path.read_text(encoding="utf-8"))
    if not isinstance(brief, dict):
        raise ValueError("Brief root must be a mapping")
    _validate_brief(brief)

    organization = str(brief["organization"]).strip()
    out_dir = out_root / _slug(organization)
    out_dir.mkdir(parents=True, exist_ok=True)

    policies_dir = out_dir / "policies"
    procedures_dir = out_dir / "procedures"
    policies_dir.mkdir(parents=True, exist_ok=True)
    procedures_dir.mkdir(parents=True, exist_ok=True)

    policy_manifest: list[dict[str, str]] = []
    for policy in brief["policies"]:
        title = str(policy.get("title", "Untitled Policy")).strip()
        slug = _slug(title)
        path = policies_dir / f"{slug}.md"
        path.write_text(_policy_doc(organization, policy), encoding="utf-8")
        policy_manifest.append({"type": "policy", "title": title, "path": str(path)})

    checklist_rows: list[dict[str, str]] = []
    procedure_manifest: list[dict[str, str]] = []
    for procedure in brief["procedures"]:
        title = str(procedure.get("title", "Untitled Procedure")).strip()
        slug = _slug(title)
        path = procedures_dir / f"{slug}.md"
        doc, rows = _procedure_doc(organization, procedure)
        path.write_text(doc, encoding="utf-8")
        checklist_rows.extend(rows)
        procedure_manifest.append({"type": "procedure", "title": title, "path": str(path)})

    with open(out_dir / "sop_checklist.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["procedure", "step_number", "step", "owner"])
        writer.writeheader()
        writer.writerows(checklist_rows)

    with open(out_dir / "manifest.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["type", "title", "path"])
        writer.writeheader()
        writer.writerows(policy_manifest + procedure_manifest)

    return BuildResult(
        output_dir=out_dir,
        policy_count=len(policy_manifest),
        sop_count=len(procedure_manifest),
    )


def main() -> None:
    args = parse_args()
    result = build_pack(Path(args.brief), Path(args.out))
    print(
        f"Built policy pack -> {result.output_dir} "
        f"(policies={result.policy_count}, procedures={result.sop_count})"
    )


if __name__ == "__main__":
    main()
