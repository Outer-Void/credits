# Attribution policy

## Licensing default
Outer Void is **proprietary by default** unless a repository is explicitly designated otherwise. Each
repository's decision is recorded in `projects/<repo>.yaml` as exactly one of:

| Decision | Meaning |
|---|---|
| `PROPRIETARY_OUTER_VOID` | Entirely Outer Void-owned, proprietary |
| `UPSTREAM_LICENSE_RETAINED` | Upstream/fork licence governs (e.g. `blhermes-agent`, MIT, Nous Research) |
| `MIXED_WITH_THIRD_PARTY_NOTICES` | Outer Void-proprietary portions plus bundled third-party material whose notices travel |
| `PUBLIC_SOURCE_PROPRIETARY` | Proprietary, but the repository is publicly visible |
| `PRIVATE_PROPRIETARY` | Proprietary and private |
| `REVIEW_REQUIRED` | An explicit other licence exists, or ownership is unconfirmed. Human decision needed |

## Rules
1. **Never blindly replace an upstream licence.** Never remove or narrow a notice that a licence requires.
   `blhermes-agent` keeps MIT (Copyright (c) 2025 Nous Research) and all 23 nested upstream licences.
2. **Never claim exclusive copyright over third-party code.** Outer Void headers go only on Outer
   Void-authored files (`templates/HEADER-POLICY.md`).
3. **Published versions keep their licence.** A repository released under Apache-2.0/MIT stays so for those
   versions. Relicensing future versions needs an owner decision and confirmation that Outer Void owns every
   contribution (`UNR-008`).
4. **Traveling notices.** Every distribution that contains third-party material ships the required texts.
   For a source tree that means `THIRD_PARTY_NOTICES.md` plus verbatim texts under `licenses/`. Built
   apps/sites must also expose them to end users (an in-app or `/third-party-notices` page) before release.
   This ledger never substitutes for them.
5. **Never rewrite history to conceal upstream origin.**
6. **Trademarks** depicted in assets (e.g. app icons) are recorded separately and imply no endorsement.

## AI assistance
Categories: `brainstorming`, `architecture_planning`, `code_generation`, `review`, `debugging`, `research`,
`documentation`, `design_asset`, `runtime`, `api_backend`, and `unspecified` (owner-reported use whose
nature has not been stated).

Evidence, strongest first:
1. commit trailers (`Co-authored-by: Claude ...`, `gemini-code-assist[bot]`) and bot authorship;
2. tool-specific branch conventions (`codex/*`), recorded as `INFERRED`;
3. owner statements (`OWNER_REPORTED`, with an `owner_declaration` source). An owner declaration is valid
   evidence of use even when repository analysis cannot infer it. It is never evidence of someone else's
   authorship.

Upstream projects' AI trailers describe upstream contributors' tooling and are not attributed to Outer Void.
AI tools are credited as assistance. They are not copyright holders, and no prompt or conversation content is
recorded.
