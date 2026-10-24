#!/usr/bin/env python3
"""Validate the Outer Void credits ledger.

Checks (each failure names the file and record):
  1. every active repository has a project record with an explicit licensing decision
  2. required notice files exist in repository checkouts (with --org-root)
  3. known vendored/upstream material has provenance lineage
  4. licence texts are not accidentally deleted or altered (licenses/CHECKSUMS.sha256)
  5. every credit reference resolves to a record
  6. unresolved provenance is visible (REVIEW_REQUIRED / UNKNOWN link to provenance/unresolved.yaml,
     and every unresolved item appears in reports/unresolved-provenance.md)
  7. SPDX licence expressions are syntactically valid and use known identifiers

Usage: tools/validate.py [--root DIR] [--org-root ~/ov] [--strict-checkouts] [--write-lock]
Exit 0 when valid, 1 with a list of problems otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Any

import yaml

RELATIONSHIPS = {
    "REQUIRED_LICENSE_NOTICE", "COPYRIGHT_HOLDER", "UPSTREAM_SOURCE", "FORK_OR_DERIVATIVE", "DEPENDENCY",
    "TOOLCHAIN", "AI_ASSISTANCE", "MODEL_OR_RUNTIME", "DATASET_SOURCE", "ASSET_SOURCE",
    "SPECIFICATION_OR_STANDARD", "DOCUMENTATION_OR_REFERENCE", "INSPIRATION", "COMMUNITY",
    "UNKNOWN_OR_REVIEW_REQUIRED",
}  # fmt: skip
DECISIONS = {
    "PROPRIETARY_OUTER_VOID", "UPSTREAM_LICENSE_RETAINED", "MIXED_WITH_THIRD_PARTY_NOTICES",
    "PUBLIC_SOURCE_PROPRIETARY", "PRIVATE_PROPRIETARY", "REVIEW_REQUIRED",
}  # fmt: skip
VERIFICATION = {"VERIFIED", "INFERRED", "OWNER_REPORTED", "REVIEW_REQUIRED"}
LINEAGE_KINDS = {"FORK_OR_DERIVATIVE", "VENDORED_COPY", "VENDORED_ASSETS", "VENDORED_BINARY", "GENERATED_FROM_TEMPLATE", "TEMPLATE"}

# SPDX identifiers accepted by this ledger (subset of https://spdx.org/licenses). Extend deliberately.
SPDX_IDS = {
    "0BSD", "Apache-2.0", "Artistic-2.0", "BSD-2-Clause", "BSD-3-Clause", "Bitstream-Vera", "BSL-1.0", "CC-BY-4.0",
    "CC-BY-SA-4.0", "CC0-1.0", "EPL-1.0", "EPL-2.0", "GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-only",
    "GPL-3.0-or-later", "ISC", "LGPL-2.1-only", "LGPL-2.1-or-later", "LGPL-3.0-only", "LGPL-3.0-or-later", "MIT",
    "MIT-0", "MIT-CMU", "MPL-2.0", "OFL-1.1", "PSF-2.0", "Python-2.0", "Ubuntu-font-1.0", "Unlicense", "Zlib",
}  # fmt: skip
SPDX_EXCEPTIONS = {"Classpath-exception-2.0", "LLVM-exception"}
LICENSE_SENTINELS = {"UNKNOWN", "NONE", "NOASSERTION"}
LICENSE_FIELDS = ("license", "spdx")
REF_FIELDS = ("affects", "refs", "credits", "surviving_obligations", "lineage", "upstream", "vendor", "source", "target", "tool", "repo", "asset")
ID_RE = re.compile(r"^[a-z]+:[A-Za-z0-9._/@:+-]+$|^(UNR|LIN|AIL)-[0-9]{3}$")
TOKEN_RE = re.compile(r"\s*(\(|\)|AND\b|OR\b|WITH\b|[A-Za-z0-9.+-]+)")


class Problems(list[str]):
    def add(self, where: str, msg: str) -> None:
        self.append(f"{where}: {msg}")


def check_spdx(expr: str) -> str | None:
    """Return an error message, or None if expr is a valid SPDX expression over known IDs."""
    if expr in LICENSE_SENTINELS:
        return None
    pos, tokens = 0, []
    while pos < len(expr):
        m = TOKEN_RE.match(expr, pos)
        if not m or m.end() == pos:
            return f"unparseable licence expression {expr!r}"
        tokens.append(m.group(1))
        pos = m.end()
        while pos < len(expr) and expr[pos] == " ":
            pos += 1
    i = 0

    def term() -> str | None:
        nonlocal i
        if i >= len(tokens):
            return "expression ends early"
        t = tokens[i]
        if t == "(":
            i += 1
            err = expression()
            if err:
                return err
            if i >= len(tokens) or tokens[i] != ")":
                return "unbalanced parenthesis"
            i += 1
            return None
        if t in ("AND", "OR", "WITH", ")"):
            return f"unexpected {t!r}"
        if not (t in SPDX_IDS or t.startswith("LicenseRef-") or (t.endswith("+") and t[:-1] in SPDX_IDS)):
            return f"unknown SPDX identifier {t!r}"
        i += 1
        if i < len(tokens) and tokens[i] == "WITH":
            i += 1
            if i >= len(tokens) or tokens[i] not in SPDX_EXCEPTIONS:
                return "WITH must be followed by a known SPDX exception"
            i += 1
        return None

    def expression() -> str | None:
        nonlocal i
        err = term()
        while not err and i < len(tokens) and tokens[i] in ("AND", "OR"):
            i += 1
            err = term()
        return err

    err = expression()
    if not err and i != len(tokens):
        err = f"trailing tokens in {expr!r}"
    return err


def load(path: Path, problems: Problems) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        problems.add(str(path), f"cannot load: {exc}")
        return None


def license_checksums(root: Path) -> str:
    files = sorted(p for p in (root / "licenses").iterdir() if p.is_file() and p.name != "CHECKSUMS.sha256")
    return "".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in files)


def validate(root: Path, org_root: Path | None = None, strict_checkouts: bool = False) -> Problems:
    problems = Problems()
    records: dict[str, tuple[str, dict[str, Any]]] = {}

    def register(rec: dict[str, Any], where: str) -> None:
        rid = rec.get("id")
        if not isinstance(rid, str) or not ID_RE.match(rid):
            problems.add(where, f"invalid id {rid!r}")
            return
        if rid in records:
            problems.add(where, f"duplicate id {rid} (also in {records[rid][0]})")
        records[rid] = (where, rec)

    sources: list[tuple[str, list[dict[str, Any]]]] = []
    for path in sorted((root / "catalog").glob("*.yaml")) + sorted((root / "provenance").glob("*.yaml")):
        doc = load(path, problems)
        if not isinstance(doc, dict) or doc.get("schema_version") != 1:
            problems.add(str(path.relative_to(root)), "missing schema_version: 1")
            continue
        (key,) = [k for k in doc if k != "schema_version"]
        items = doc[key] or []
        sources.append((str(path.relative_to(root)), items))
        for rec in items:
            if "id" in rec:
                register(rec, str(path.relative_to(root)))
    projects: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "projects").glob("*.yaml")):
        doc = load(path, problems)
        rec = (doc or {}).get("project")
        where = str(path.relative_to(root))
        if not isinstance(rec, dict):
            problems.add(where, "missing project record")
            continue
        register(rec, where)
        projects[rec["id"]] = rec
        sources.append((where, [rec]))

    unresolved_ids = {i for i, (w, _) in records.items() if i.startswith("UNR-")}

    # 5/6/7: per-record checks
    for where, items in sources:
        for rec in items:
            label = f"{where}:{rec.get('id') or rec.get('repo') or rec.get('asset')}"
            for rel in rec.get("relationship", []) or []:
                if rel not in RELATIONSHIPS:
                    problems.add(label, f"unknown relationship class {rel}")
            ver = rec.get("verification")
            if ver is not None and ver not in VERIFICATION:
                problems.add(label, f"unknown verification {ver}")
            for field in LICENSE_FIELDS:
                if isinstance(rec.get(field), str):
                    err = check_spdx(rec[field])
                    if err:
                        problems.add(label, f"{field}: {err}")
            for field in REF_FIELDS:
                vals = rec.get(field)
                for v in [vals] if isinstance(vals, str) else (vals or []):
                    if v == "*" and field == "affects":
                        continue
                    if v not in records:
                        problems.add(label, f"{field} -> unresolved reference {v!r}")
            unr = rec.get("unresolved")
            unr_list = [unr] if isinstance(unr, str) else (unr or [])
            for u in unr_list:
                if u not in unresolved_ids:
                    problems.add(label, f"unresolved -> unknown item {u!r}")
            needs = ver == "REVIEW_REQUIRED" or any(rec.get(f) in ("UNKNOWN", "NOASSERTION") for f in LICENSE_FIELDS) or (
                "UNKNOWN_OR_REVIEW_REQUIRED" in (rec.get("relationship") or [])
            )
            if needs and not unr_list:
                problems.add(label, "REVIEW_REQUIRED/UNKNOWN must link to an unresolved item")
            if rec.get("decision") == "REVIEW_REQUIRED" and not unr_list:
                problems.add(label, "REVIEW_REQUIRED decision must link to an unresolved item")
            lf = rec.get("license_file")
            if lf and not (root / lf).is_file():
                problems.add(label, f"license_file missing: {lf}")

    # 1: every active repository has a decision
    repo_map = load(root / "provenance" / "repository-map.yaml", problems) or {}
    for entry in repo_map.get("repositories", []):
        rid = entry["repo"]
        rec = projects.get(rid)
        if rec is None:
            problems.add("provenance/repository-map.yaml", f"{rid} has no projects/ record")
            continue
        if rec.get("decision") not in DECISIONS:
            problems.add(f"projects:{rid}", f"decision {rec.get('decision')!r} is not one of {sorted(DECISIONS)}")
        for f in ("current_license", "intended_license", "traveling_notices", "surviving_obligations"):
            if f not in rec:
                problems.add(f"projects:{rid}", f"missing {f}")
    for rid in projects:
        if rid not in {e["repo"] for e in repo_map.get("repositories", [])}:
            problems.add(f"projects:{rid}", "not listed in provenance/repository-map.yaml")

    # 3: lineage coverage
    for lid, (where, rec) in records.items():
        if not lid.startswith("LIN-"):
            continue
        if rec.get("kind") not in LINEAGE_KINDS:
            problems.add(f"{where}:{lid}", f"unknown lineage kind {rec.get('kind')}")
        target = projects.get(rec.get("target", ""))
        if target is not None and lid not in (target.get("lineage") or []):
            problems.add(f"{where}:{lid}", f"target {rec['target']} does not list this lineage")
    for _rid, (where, rec) in records.items():
        if "FORK_OR_DERIVATIVE" in (rec.get("relationship") or []):
            if not any(r.get("source") == rec["id"] for i, (_, r) in records.items() if i.startswith("LIN-")):
                problems.add(f"{where}:{rec['id']}", "fork/derivative source without a lineage record")

    # 4: licence text lock
    lock = root / "licenses" / "CHECKSUMS.sha256"
    if not lock.is_file():
        problems.add("licenses/", "CHECKSUMS.sha256 missing")
    elif lock.read_text(encoding="utf-8") != license_checksums(root):
        problems.add("licenses/CHECKSUMS.sha256", "licence texts were added, removed or changed; review, then --write-lock")

    # 6: unresolved items must be visible in the human report
    report = root / "reports" / "unresolved-provenance.md"
    text = report.read_text(encoding="utf-8") if report.is_file() else ""
    for u in sorted(unresolved_ids):
        if u not in text:
            problems.add("reports/unresolved-provenance.md", f"{u} is not listed")

    # 2: traveling notices in checkouts
    if org_root is not None:
        for rid, rec in projects.items():
            checkout = Path(str(rec.get("path", "")).replace("~/ov", str(org_root)))
            if not checkout.is_dir():
                if strict_checkouts:
                    problems.add(f"projects:{rid}", f"checkout not found at {checkout}")
                continue
            for notice in rec.get("traveling_notices") or []:
                if not (checkout / notice).is_file():
                    problems.add(f"projects:{rid}", f"required notice missing in checkout: {notice}")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--org-root", type=Path, help="directory containing the repository checkouts (e.g. ~/ov)")
    ap.add_argument("--strict-checkouts", action="store_true", help="fail if a checkout is missing")
    ap.add_argument("--write-lock", action="store_true", help="record licence text checksums after review")
    args = ap.parse_args(argv)
    if args.write_lock:
        (args.root / "licenses" / "CHECKSUMS.sha256").write_text(license_checksums(args.root), encoding="utf-8")
        return 0
    problems = validate(args.root, args.org_root, args.strict_checkouts)
    for p in problems:
        print(p, file=sys.stderr)
    print(f"credits validation: {'OK' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
