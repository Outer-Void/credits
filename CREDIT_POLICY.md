# Credit policy

1. **Be generous, be accurate.** Credit every identifiable source of code, architecture, ideas, tooling,
   models, datasets, libraries, assets, documentation, inspiration and assistance, but only as what it
   actually was.
2. **Credit is not endorsement.** No record implies endorsement, sponsorship, affiliation, partnership or
   authorship by the credited party. Vendor names (OpenAI, Anthropic, Google, DeepSeek, Meta, Nous Research,
   and others) identify tools and sources only.
3. **Credit is not derivation.** An `INSPIRATION`, `DOCUMENTATION_OR_REFERENCE` or `SPECIFICATION_OR_STANDARD`
   record says nothing about copied code. Code derivation is recorded only as `UPSTREAM_SOURCE` /
   `FORK_OR_DERIVATIVE` with a lineage record.
4. **Named people only from authoritative evidence.** Sources include:
   - copyright lines, licence files and AUTHORS/CONTRIBUTORS files;
   - public git authorship;
   - official project documentation and histories;
   - foundations and specification bodies;
   - original publications;
   - maintainer documentation.

   Each claim records its source and the excerpt that supports it. A role is stated only as strongly as its
   source states it: "led the development of" is not "created", and "co-founded the company" is not
   "created the tool". When authorship is broad or uncertain, credit the project, organization or
   community, and record the open question as an `UNR-` item. Git identities are recorded as written.
   Aliases are not merged and roles are not inferred.
5. **Private repositories.** This ledger is public. Records for private repositories carry only public-safe
   facts. Contributor names from private history are withheld until consent is confirmed.
6. **AI assistance** is recorded per [ATTRIBUTION_POLICY](ATTRIBUTION_POLICY.md#ai-assistance), with evidence,
   and without prompts, conversations, secrets or personal data.
7. **Absence of evidence** is recorded as `REVIEW_REQUIRED` with an `UNR-` item, never as a negative claim
   and never as a guessed positive claim.

8. **Collective work is credited collectively.** A technology credited to named individuals also credits
   the community, host or steward behind it, unless it genuinely has a single author
   (`authorship: individual`).
9. **History is kept.** Records are never deleted. Use `status` (`historical`, `replaced`, `migrated`,
   `deprecated`, `upstream_origin`, `former_development_tooling`) when something is no longer current.

See [GOVERNANCE.md](GOVERNANCE.md) for the governing principle and the Definition of Done.

## Roles and statuses
Attribution-graph edges and records with `roles` use this vocabulary:

| Group | Roles |
|---|---|
| People and organizations behind a work | `creator`, `co_creator`, `founder`, `co_founder`, `original_author`, `author`, `editor`, `developer`, `maintainer`, `contributor`, `copyright_holder`, `steward`, `host`, `community` |
| How a work relates to Outer Void | `upstream_source`, `fork_origin`, `nested_upstream`, `dependency`, `transitive_dependency`, `bundled_component`, `vendored_component`, `development_tool`, `build_tool`, `test_tool`, `ci_infrastructure`, `runtime`, `language`, `platform`, `operating_system`, `package_ecosystem`, `infrastructure`, `ai_assistance`, `model`, `model_runtime`, `research`, `standard`, `specification`, `dataset`, `inspiration`, `architectural_influence`, `documentation_reference`, `legal_attribution`, `historical_lineage` |

A role is extended in `tools/attribution.py` when a real contribution does not fit. Nobody's contribution is
bent to fit an existing role.

## Relationship classes
`REQUIRED_LICENSE_NOTICE`, `COPYRIGHT_HOLDER`, `UPSTREAM_SOURCE`, `FORK_OR_DERIVATIVE`, `DEPENDENCY`, `TOOLCHAIN`,
`AI_ASSISTANCE`, `MODEL_OR_RUNTIME`, `DATASET_SOURCE`, `ASSET_SOURCE`, `SPECIFICATION_OR_STANDARD`,
`DOCUMENTATION_OR_REFERENCE`, `INSPIRATION`, `COMMUNITY` and `UNKNOWN_OR_REVIEW_REQUIRED`.
A record may carry several classes. "Inspired by" credit (`INSPIRATION`) and legally required notice
(`REQUIRED_LICENSE_NOTICE`) are always separate.
