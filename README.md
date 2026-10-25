# Outer Void Credits

The canonical attribution, licensing and provenance ledger for every Outer Void repository and product.

> **Outer Void is proprietary by default. Third-party rights remain third-party rights. Attribution is
> preserved beyond the minimum legal requirement where provenance is known.**

This repository **supplements, but never replaces**, the notices and licences that must travel with each
source tree, package, binary, app, site, model, dataset or asset. Those stay in the individual repositories
(`LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `licenses/`).

## Layout
| Path | Contents |
|---|---|
| [`ACKNOWLEDGMENTS.md`](ACKNOWLEDGMENTS.md) | Human-readable acknowledgments, generated from the data |
| [`GOVERNANCE.md`](GOVERNANCE.md) | "We acknowledge the shoulders we stand on": the permanent rule and the Definition of Done |
| `catalog/` | Stable-ID records: people, communities, organizations, projects, tools, AI, models, libraries, datasets, assets, standards, inspirations |
| `projects/` | One record per Outer Void repository: licence decision, obligations, traveling notices, unresolved items |
| `licenses/` | Verbatim third-party licence texts (locked by `CHECKSUMS.sha256`) |
| `provenance/` | Repository map, source lineage (incl. Hermes → BLHERMES), attribution graph, AI-assistance ledger, asset lineage, append-only id ledger, unresolved items |
| `reports/` | Attribution audit, licence compatibility, unresolved provenance |
| `templates/` | Outer Void proprietary licence and source-header policy (not applied blindly) |
| `tools/` | `validate.py` (ledger checks), `render_unresolved.py` |

## IDs
`<kind>:<slug>`, for example `repo:void-os`, `org:nous-research`, `lib:pypi/jsonschema`,
`asset:font/fira-code`, `ai:claude-code`. Also `UNR-nnn` (unresolved), `LIN-nnn` (lineage) and `AIL-nnn`
(AI ledger) and `ATT-nnn` (attribution-graph edges). IDs are never reused or deleted (`provenance/id-ledger.txt`). A repository can cite a record as `credits:<id>`.

## Verification states
`VERIFIED` (primary evidence inspected), `INFERRED` (strong indirect evidence), `OWNER_REPORTED`, and
`REVIEW_REQUIRED`. Licences that cannot be established are `UNKNOWN` or `NOASSERTION`. They are never guessed,
and they always link to an `UNR-` item.

## Validate
```sh
pip install PyYAML
python tools/validate.py                    # ledger consistency
python tools/validate.py --org-root ~/ov    # plus: required notices and ov: evidence exist in each checkout
python tools/render_acknowledgments.py      # regenerate ACKNOWLEDGMENTS.md (validation fails if stale)
python -m unittest discover -s tests
```

Policies: [CREDIT_POLICY](CREDIT_POLICY.md) · [ATTRIBUTION_POLICY](ATTRIBUTION_POLICY.md) ·
[PROVENANCE_POLICY](PROVENANCE_POLICY.md) · [CONTRIBUTING](CONTRIBUTING.md)

This ledger is attribution and provenance infrastructure. It is **not legal advice** and does not replace
professional review before commercial distribution.
