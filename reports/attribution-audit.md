# Attribution audit: Stage 01A (2026-10-24)

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
