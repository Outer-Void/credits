# Attribution audit

## Comprehensive attribution pass (Stage 08 directive, 2026-10-25)

Scope: every repository in `provenance/repository-map.yaml` (31). The one non-repository directory under
`~/ov` stays uninspected by owner instruction (`UNR-015`). The pass went beyond licences to people,
communities, technological lineage, AI assistance and inspiration ([GOVERNANCE.md](../GOVERNANCE.md)).

### Method

1. **Discovery.** A read-only scan of every checkout covered:
   - Python, npm and Gradle manifests;
   - GitHub Actions `uses:` lines;
   - Dockerfiles and shebang interpreters;
   - licence, notice, AUTHORS and CONTRIBUTORS files;
   - `Co-authored-by` trailers and bot authors;
   - AI and technology mentions in documentation.

   Its results were compared with the catalog.
2. **Research.** Each candidate attribution was checked against an authoritative source: licence and AUTHORS
   files, official histories, maintainer documentation, foundations, RFCs and specifications. A claim was
   kept only if the fetched page contained the stated name or fact. 110 distinct URLs on 41 domains were
   fetched, and the matched excerpts are stored with each edge.
3. **Roles worded to the evidence.** For example:
   - Linus Torvalds is credited as *developer* of Git ("the Linux development community, and in
     particular Linus Torvalds"), not as its sole creator;
   - Hans Dockter as *co-founder of Gradle, Inc.*, not as creator of the build tool;
   - Kotlin only to JetBrains, because no designer role was verified.
4. **Owner declarations.** The owner confirmed use of ChatGPT, DeepSeek, BLACKBOX AI and Meta Llama models.
   These are recorded as `OWNER_REPORTED`.

### Added

| | |
|---|---|
| People | 65 (creators, original authors, maintainers, specification authors and editors, copyright holders of nested upstream work) |
| Communities | 44 (new `catalog/communities.yaml`) |
| Organizations | 19 |
| Technologies and tools | 21 tools, 8 libraries, 7 standards |
| Projects | 19 (Anthropic's claude-plugins-official, and the 18 nested upstream components of Hermes Agent) |
| Attribution-graph edges | 232 (183 VERIFIED, 45 INFERRED, 4 OWNER_REPORTED) |
| Unresolved items | 2 new (UNR-017 originators not yet verified, UNR-018 scope of owner-reported AI use); UNR-011 and UNR-012 resolved by owner declaration |

Major lineages now credited:
- **Python:** Guido van Rossum, CWI, the PSF, the CPython community; PyPA; PyPI.
- **GNU:** Richard Stallman, the FSF, the GNU Project; Bash (Brian Fox, Chet Ramey); zsh (Paul Falstad).
- **Linux:** Linus Torvalds, the kernel community, the Linux Foundation.
- **Git:** Linus Torvalds, Junio C Hamano, the Git community.
- **Debian:** Ian Murdock, the Debian Project.
- **Java:** the JLS authors, Oracle, OpenJDK.
- **Kotlin and Gradle:** JetBrains; Gradle, Inc. and the Gradle community.
- **Android:** AOSP and the Android Gradle plugin.
- **Termux and PRoot:** Termux; PRoot (Cédric Vincent).
- **GitHub and CI:** GitHub and the CI actions Outer Void uses.
- **Python libraries:** jsonschema, PyYAML, pytest, mypy, Ruff, Hypothesis, Requests, Rich, Typer and FastAPI.
- **JavaScript:** Node.js, npm, React, Next.js, Vite, Tailwind CSS, ESLint and TypeScript.
- **Other tools:** zlib, GnuPG, Docker.
- **Standards:** JSON Schema, JSON, YAML, TOML, SemVer, RFC 3339, SARIF, SPDX, SHA-256 and Unicode
  normalization; the unified diff format (Wayne Davison) and the GNU diff authors.
- **llama.cpp:** the ggml authors and ggml.ai.
- **Hermes Agent:** Nous Research, its upstream contributors and its 18 nested component licences.

### Findings and fixes

1. **The BLHermes rebrand had altered upstream notices.** Commit 23a035474c changed "Hermes" to "BLHermes"
   in four upstream attribution files:
   - the MIT copyright line in `plugins/hermes-achievements/LICENSE`;
   - the Apache-2.0 attribution notice in `plugins/security-guidance/NOTICE`;
   - two contributor-attribution records.

   All four were restored byte-for-byte to the upstream fork point in blhermes-agent ac51a44f1f.
2. **Nested upstream licences were only counted.** They are now 18 records with their copyright holders, each
   with a `legal_attribution` edge to BLHermes. The earlier count of 23 included non-licence files.
3. **A product name parsed as a YAML mapping** in `projects/blux-coga.yaml` and rendered as `{...}`. It is
   now quoted, and validation rejects non-string names.
4. **A duplicate identity** (a second "ggml authors" record) was caught by the new duplicate check and merged
   into `org:ggml`.

### Remaining research gaps

- **Originators not yet verified** (UNR-017):
  - Termux's original author;
  - Kotlin's language designers;
  - JUnit 4's authors;
  - the ULID author;
  - Android Inc.'s founders;
  - Node.js's and React's original authors;
  - GitHub's founders;
  - npm's operator.
- **AI use not yet scoped** (UNR-018): which repositories, and what kind of help, for the owner-reported AI
  systems.
- **Package licences still unchecked:** individual Maven/npm transitive dependencies beyond those already
  catalogued (`lib:blhermes-dependency-graph` covers the fork's tree collectively).
- **Possible code derivation:** a deeper per-file pass for copied snippets, beyond licence and notice files.
- **One source currently refuses automated fetches:** chatgpt.com (its excerpt matched on 2026-10-25 and the
  page later returned 403).

All currently identifiable and evidence-supported contributors, technologies, projects, organizations,
communities, tools and inspirations found by this documented pass are recorded, and the remaining gaps are
tracked above and in [unresolved-provenance.md](unresolved-provenance.md).

---

# Stage 01A attribution audit (2026-10-24)

## Scope
31 repositories: the 30 baselined in Stage 00 plus `credits`, covering `~/ov` and `~/ov/ov-webpages`.

Inspected:
- LICENSE, COPYING, NOTICE, AUTHORS, CREDITS and third-party files;
- READMEs, git remotes and history, author and committer identities, `Co-authored-by` trailers, PR branch names;
- foreign copyright headers and non-org upstream URLs;
- manifests and lockfiles;
- bundled binaries, fonts and media;
- model, provider and AI references.

Non-repository directories under `~/ov` were not inspected (`UNR-015`).

## Method
| Evidence | How it was verified |
|---|---|
| Python licences | `dist-info/METADATA` of installed packages (Stage 00/01 audit venvs) |
| Maven licences | `<license>` in cached POMs |
| npm licences | `license` field and LICENSE file of the exact installed version |
| Fonts | OpenType `name` table IDs 0, 13 and 14, read with fontTools |
| libGDX natives | SHA-256 of committed `libgdx.so` against the `gdx-platform-1.12.1` natives jar |
| Upstream licence texts | Fetched from apache.org, spdx/license-list-data and the upstream repositories |
| AI assistance | Commit trailers, bot authors and `codex/*` PR branches |

## Key findings
1. **void.os bundles 41 fonts with no licence texts in the repository.**
   - Verified: OFL-1.1 (34), Hack MIT + Bitstream Vera (2), Ubuntu Font Licence 1.0 (2).
   - Unverifiable from file metadata: Meslo LGS NF, Mononoki NF, Victor Mono NF (`UNR-002`). Monaspace states OFL-1.1 but has no copyright notice.
   - Nerd Fonts glyph-set notices are not enumerated (`UNR-003`).
   - `cascadia_code.ttf` is actually CaskaydiaCove NF.
   - **Notices added in Stage 01A.**
2. **void.game commits libGDX 1.12.1 native binaries** (Apache-2.0, byte-identical to upstream). **Apache-2.0 notice added.**
3. **blux10k `.p10k.zsh` is generated from powerlevel10k's `p10k-lean.zsh`** (MIT). **MIT notice added.**
4. **Built sites bundle MIT runtimes:**
   - theresolver: Next.js 16.1.6, React 19.2.3;
   - roughin: React 18.3.1, React Router 6.30.6, axios 1.20.0, Workbox 7.4.1.

   **Notices added.** End-user-visible notices are still needed before release.
5. **Android apps bundle AndroidX, Kotlin stdlib and the Gradle wrapper** (Apache-2.0). Notices were added to void.os, void.game, void.sys and termux-background. voidforge already had them.
6. **blhermes-agent is an MIT fork of NousResearch/hermes-agent.**
   - It keeps 23 nested upstream licences.
   - It is 14 commits past merge base `3fa571a5`, touching 4,257 files.
   - Upstream main moved to `5894e750`.
   - Lineage: `LIN-001`.
7. **termux-background references termux-app and Termux:Monet (both GPL-3.0) as interfaces only.** No code was copied. Keep that boundary.
8. **AI assistance with evidence:**
   - OpenAI Codex: 18 repos, 123 merged PRs from `codex/*` branches (INFERRED);
   - Claude Sonnet 4.6: void.os, void.game, void.sys, resolver;
   - Claude Opus 5.5 / Claude Code: blux, credits;
   - Gemini Code Assist: resolver;
   - GitHub Copilot coding agent: theresolver;
   - Copilot Autofix: god;
   - Dependabot: resolver.

   **No evidence** of development use for ChatGPT (beyond 3 mentions), DeepSeek, BLACKBOX AI or Meta Llama (`UNR-011`). DeepSeek, OpenAI and Anthropic models are **runtime/API backends** of blux-gpt and resolver.
9. **BLACKBOX AI, ChatGPT, Claude, Gemini, Copilot and Perplexity appear as brand marks in VOID.SYS icons.** This is a trademark review item (`UNR-004`), not a credit for assistance.
10. **Public visibility of proprietary code:** 11 public repositories carry proprietary or all-rights-reserved licences (`UNR-014`).

## Counts
| Category | Records |
|---|---|
| Organizations | 24 |
| People (authoritative evidence only) | 9 |
| Upstream projects | 5 |
| Tools / toolchain | 16 |
| AI tools | 9 |
| Models / runtimes | 7 |
| Libraries (direct) | 88 |
| Datasets | 4 |
| Assets | 49 |
| Standards | 10 |
| Inspirations | 4 |
| Repository records | 31 |
| AI ledger entries | 34 |
| Unresolved items | 16 |

See `license-compatibility.md` and `unresolved-provenance.md`.
