from pathlib import Path

from src.build_policy_pack import build_pack


def test_build_pack_outputs_docs(tmp_path: Path) -> None:
    brief = tmp_path / "brief.yaml"
    brief.write_text(
        """
organization: Demo Org
policies:
  - title: Access Policy
    purpose: Control access
    scope: All users
procedures:
  - title: Onboarding
    trigger: New hire
    steps:
      - Create account
""".strip()
    )

    result = build_pack(brief, tmp_path / "out")
    assert result.policy_count == 1
    assert result.sop_count == 1
    assert (result.output_dir / "manifest.csv").exists()
    assert (result.output_dir / "sop_checklist.csv").exists()
