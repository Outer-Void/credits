# Licence compatibility: Stage 01A (2026-10-24)

Not legal advice. These are engineering findings to support review by counsel.

## Bundled third-party material in proprietary products
| Product | Material | Licence | Compatible with proprietary distribution? | Conditions |
|---|---|---|---|---|
| AXIOM Launcher (void.os) | 34 OFL fonts | OFL-1.1 | Yes, bundled with software | Include OFL text + copyright. Do not sell fonts by themselves. Respect Reserved Font Names if modified |
| AXIOM Launcher | Hack, Hack NF | MIT AND Bitstream-Vera | Yes | Include both notices. Bitstream Vera: no standalone sale, renaming rules |
| AXIOM Launcher | Ubuntu Mono (NF) | Ubuntu-font-1.0 | Yes | Include licence. Modified versions must be renamed |
| AXIOM Launcher | Meslo, Mononoki, Victor Mono (NF) | **UNKNOWN** | **Unverified** | `UNR-002`. Do not ship until resolved |
| AXIOM Launcher | Nerd Fonts glyph sets | mixed | Likely, per set | `UNR-003` |
| AXIOM Launcher / Shooter | libGDX 1.12.1 / 1.14.2 | Apache-2.0 | Yes | Include licence. No NOTICE file is shipped in the gdx jar |
| Android apps | AndroidX, Kotlin stdlib, coroutines | Apache-2.0 | Yes | Include licence |
| Roughin frontend, TheResolverBot site | React, Next.js, React Router, axios, Workbox | MIT | Yes | Retain copyright + permission notice in distributed bundles |
| blux10k | p10k-derived config | MIT | Yes | Retain notice |

## Upstream-licensed code
| Repo | Licence | Finding |
|---|---|---|
| blhermes-agent | MIT (Nous Research) + nested licences | Proprietary BLUX may incorporate MIT code if the MIT notice travels with every copy or substantial portion. Each nested skill/plugin licence must be checked before that component is moved (`UNR-001`) |
| termux-background | MIT (holder unclear, `UNR-007`) | Targets GPL-3.0 projects' interfaces only. **Copying termux-app or Termux:Monet code would require GPL-3.0 for the combined work. Do not.** |

## Incompatibilities / risks found
- **None proven.** No GPL/AGPL code was found inside a proprietary distribution.
- **Risks:**
  - unverified font licences (`UNR-002`);
  - Nerd Fonts glyph sets (`UNR-003`);
  - brand marks in a paid icon pack (`UNR-004`);
  - artwork of unknown origin (`UNR-005`);
  - non-owner authorship of operationrestore (`UNR-006`);
  - Python packages whose licence is ambiguous from metadata (`UNR-016`). These are runtime-installed, not bundled.
- **Test-only EPL-1.0** (JUnit 4) is not distributed.

## Relicensing constraints
Repositories under Apache-2.0 or MIT (`UNR-008`) cannot have **already-published** versions withdrawn from
those licences. Relicensing future versions needs:
1. an owner decision;
2. confirmation that all contributions are Outer Void-owned;
3. a decision on AI-assisted contributions under the AI providers' terms.

god-cli 1.0.1 is on PyPI under MIT.
