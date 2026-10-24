# Provenance policy

1. **Evidence first.** Each record lists the evidence inspected: licence file, package metadata, POM,
   font `name` table, file hash, git trailer, or upstream URL. Without evidence, the record is
   `REVIEW_REQUIRED` and links to `provenance/unresolved.yaml`.
2. **Vendored and upstream material needs lineage.** Copies, forks, binaries, generated-from-template files
   and bundled assets get a `LIN-` record in `provenance/source-lineage.yaml`. The target repository's
   project record lists it.
3. **Unknown stays visible.** `reports/unresolved-provenance.md` is generated from the data and lists every
   open item with its owner.
4. **Hashes over names.** Where practical, identity is proven by content: libGDX natives in void.game match
   `gdx-platform-1.12.1` byte for byte.
5. **BLHERMES → BLUX** (`LIN-001`):
   - Stage 11 refines file/subsystem lineage during migration.
   - Stage 16 audits it.
   - Stage 17 may not retire BLHERMES until the MIT notice, the nested upstream licences and this lineage
     survive independently in every successor distribution.
6. **Private data.** Public records exclude private repository internals (environment names, internal hosts,
   identifiers) and private contributors' identities.
7. **Changes** to `licenses/` require review and `tools/validate.py --write-lock`. Accidental deletion
   fails validation.
