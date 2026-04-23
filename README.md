# policy-procedure-writer-os

Generate policy and SOP document packs from structured briefs.

## What it does
- Builds policy markdown docs
- Builds procedure (SOP) markdown docs
- Exports SOP checklist CSV and document manifest

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/build_policy_pack.py --brief examples/brief.yaml --out out
```

## Outputs
- `out/<org-slug>/policies/*.md`
- `out/<org-slug>/procedures/*.md`
- `out/<org-slug>/sop_checklist.csv`
- `out/<org-slug>/manifest.csv`
