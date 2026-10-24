# Contributing to the credits ledger

1. Add or update a record in the right `catalog/*.yaml` file. Use a new stable ID (`<kind>:<slug>`) and never
   reuse or renumber one.
2. Cite evidence. If you cannot verify a licence or origin, set `REVIEW_REQUIRED` / `UNKNOWN` and add an
   `UNR-` item to `provenance/unresolved.yaml`.
3. Vendored, forked or generated material: add a `LIN-` record and list it in the target `projects/` record.
4. New third-party licence text: add it verbatim under `licenses/` from an authoritative source, then
   `python tools/validate.py --write-lock`.
5. Regenerate `python tools/render_unresolved.py`, then run `python tools/validate.py --org-root ~/ov` and
   `python -m unittest discover -s tests`.
6. Never add prompts, conversations, secrets, credentials or private personal data.

A repository's own `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md` and `licenses/` stay in that repository.
Updating this ledger never replaces them.
