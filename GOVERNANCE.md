# Governance: attribution and academic integrity

This is a permanent Outer Void governance rule. It applies to every stage of the Outer Void Master
Integration & Execution Plan, and to every repository, product, tool, model, dataset, service, artifact,
dependency and integration in the Outer Void ecosystem. Only the Outer Void project owner can supersede it.

> **WE ACKNOWLEDGE THE SHOULDERS WE STAND ON.**
>
> Outer Void recognizes that meaningful engineering is built upon generations of prior work. We make a
> reasonable, evidence-based effort to acknowledge the people, communities, projects, technologies,
> research, tools, infrastructure, models, standards, and ideas that enabled or influenced our work. We
> preserve legally required attribution and voluntarily acknowledge meaningful intellectual contributions
> beyond those requirements. We distinguish authorship from inspiration, dependency from influence, and
> evidence from assumption. We do not erase historical contribution simply because our implementation
> evolves.

## What this means in practice

1. **Legal attribution is the floor, not the goal.** If an identifiable person, community, organization,
   project, technology, model, dataset, publication, standard or idea materially contributed to, enabled,
   influenced, inspired, supported or provided infrastructure, tooling or intellectual foundations for Outer
   Void work, we make an evidence-based effort to credit it here, whether or not a licence requires it.
2. **Credit is accurate.** Each acknowledgment says what the contribution actually was: creator, maintainer,
   steward, dependency, tool, inspiration and so on. The roles are defined in
   [CREDIT_POLICY](CREDIT_POLICY.md#roles-and-statuses). Collective work credits its community, not a lone
   individual. An inspiration is not a dependency, and acknowledgment implies no endorsement.
3. **Credit is evidenced.** Sources, in order of preference:
   1. original repositories;
   2. project documentation;
   3. source headers;
   4. AUTHORS and CONTRIBUTORS files;
   5. foundations;
   6. original publications;
   7. specification bodies;
   8. official histories;
   9. maintainer documentation;
   10. the owner's own declarations.

   Every claim records its source, and a URL source records the matched excerpt and the date it was
   checked.
4. **Nothing is invented.** A person's role is never guessed, and an association is never promoted to
   authorship. Attribution that seems likely but cannot be established yet is recorded as an open
   [unresolved item](reports/unresolved-provenance.md), never asserted.
5. **Legal notices stay separate and intact.** Required notices travel with the repositories that ship the
   work. A voluntary credit never replaces one, and third-party licence text is never altered.
6. **History is kept.** A credit is marked historical, replaced, migrated or deprecated, never deleted.
   `provenance/id-ledger.txt` makes a deleted id fail validation.
7. **Private work stays private.** Records about private repositories carry only public-safe facts.

## Definition of Done (every stage, every repository change)

A stage or change is not done until attribution has been reviewed. It needs review whenever it introduces,
or stops using:

- a dependency;
- an upstream project;
- copied or adapted source;
- a vendored component or bundled asset;
- a development tool;
- an AI system;
- a model or runtime;
- a dataset;
- a framework;
- a major architectural inspiration.

When a credit is due, update this repository in the same stage:

1. Add or update the records and the [attribution graph](provenance/attribution-graph.yaml) edges, with
   sources.
2. Record anything that cannot be verified yet as an unresolved item.
3. Run `python tools/validate.py --write-id-ledger`, then the renderers (`tools/render_acknowledgments.py`
   and `tools/render_unresolved.py`).
4. Run `python tools/validate.py --org-root ~/ov` and `python -m unittest discover -s tests`.
5. Report what was credited and which gaps remain. Never claim that all contributors have been credited.

## Where things are

| | |
|---|---|
| [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md) | human-readable acknowledgments, generated from the data |
| [provenance/attribution-graph.yaml](provenance/attribution-graph.yaml) | who created, maintains, stewards or hosts what, and how works relate to Outer Void |
| `catalog/` | people, communities, organizations, technologies, AI, models, datasets, assets, standards, inspirations |
| [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), `licenses/` | legal notices (separate from voluntary credit) |
| [reports/unresolved-provenance.md](reports/unresolved-provenance.md) | what we could not verify yet, and who owns finding out |
