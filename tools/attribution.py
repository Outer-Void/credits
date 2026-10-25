"""Attribution checks added for the comprehensive-attribution directive (GOVERNANCE.md).

These run inside tools/validate.py, after the original ledger checks, which are unchanged:

  A. vocabulary: `roles`, `status` and source `kind` values come from the lists below
  B. sources: every attribution-graph edge, and every record with `roles`, cites sources;
     URLs are https, local references resolve, checked dates are ISO dates
  C. evidence strength: authorship roles (creator, founder, original author ...) need an
     authoritative source, never an owner declaration alone; OWNER_REPORTED needs an owner declaration
  D. no sole credit for collective work: a technology (tool/lib/std/model) credited to individual authors
     must also credit the community, host, steward or contributors behind it, unless its record states
     `authorship: individual`
  E. contradictions: the same subject/object pair cannot be both inspiration and code lineage,
     or carry one role with two statuses
  F. unresolved items shown as verified: VERIFIED with an open unresolved item needs `verified_scope`;
     and no record may still link an item that is resolved
  G. duplicate identities across people, organizations and communities (normalized names)
  H. orphans: people and communities must be credited for something
  I. schema drift: record fields must be known for their file
  J. history: provenance/id-ledger.txt lists every id ever issued; none may disappear
  K. legal attribution: legal_attribution edges cite a licence or notice file; required notices are stated
  L. ACKNOWLEDGMENTS.md is current
"""

from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

ROLES = {
    # people and organizations behind a work
    "creator", "co_creator", "founder", "co_founder", "original_author", "author", "editor", "developer",
    "maintainer", "contributor", "copyright_holder", "steward", "host", "community",
    # how a work relates to Outer Void
    "upstream_source", "fork_origin", "nested_upstream", "dependency", "transitive_dependency",
    "bundled_component", "vendored_component", "development_tool", "build_tool", "test_tool",
    "ci_infrastructure", "runtime", "language", "platform", "operating_system", "package_ecosystem",
    "infrastructure", "ai_assistance", "model", "model_runtime", "research", "standard", "specification",
    "dataset", "inspiration", "architectural_influence", "documentation_reference", "legal_attribution",
    "historical_lineage",
}  # fmt: skip
STATUS = {"current", "historical", "replaced", "migrated", "deprecated", "upstream_origin", "former_development_tooling"}
SOURCE_KINDS = {
    "repository", "documentation", "source_header", "authors_file", "license_file", "notice_file", "foundation",
    "publication", "specification", "official_history", "maintainer_documentation", "owner_declaration",
    "package_metadata", "git_history", "website",
}  # fmt: skip
AUTHORSHIP = {"creator", "co_creator", "founder", "co_founder", "original_author"}
INDIVIDUAL_CREDIT = AUTHORSHIP | {"author", "developer", "copyright_holder", "editor"}
COLLECTIVE = {"community", "contributor", "steward", "host", "maintainer"}
INFLUENCE = {"inspiration", "architectural_influence"}
CODE_LINEAGE = {"upstream_source", "fork_origin", "nested_upstream", "vendored_component", "bundled_component", "dependency"}
UNRESOLVED_STATUS = {"open", "resolved"}

COMMON = {"id", "name", "relationship", "roles", "status", "affects", "evidence", "sources", "verification",
          "verified_scope", "unresolved", "notes", "refs", "url", "license", "aliases", "authorship"}  # fmt: skip
KNOWN_KEYS: dict[str, set[str]] = {
    "ai": COMMON | {"assistance", "vendor"},
    "ai-assistance": {"id", "tool", "repo", "commits", "categories", "evidence", "verification",
                      "merged_prs_from_codex_branches", "sources", "notes"},
    "asset-lineage": {"asset", "evidence", "file", "license", "unresolved", "upstream", "verification"},
    "assets": COMMON | {"file", "font_version", "license_file", "required_notice", "shipped", "upstream"},
    "communities": COMMON,
    "datasets": COMMON,
    "inspirations": COMMON,
    "libraries": COMMON | {"ecosystem", "license_as_declared", "license_file", "required_notice", "shipped", "spdx",
                           "version", "versions_cached", "versions_observed", "upstream"},
    "models": COMMON | {"license_file", "shipped", "vendor"},
    "organizations": COMMON | {"required_notice"},
    "people": COMMON,
    "projects": COMMON | {"license_file", "required_notice", "shipped", "upstream", "vendor", "path", "copyright",
                          "obligations"},
    "repository-map": {"path", "products", "repo", "upstream", "visibility"},
    "source-lineage": {"facts", "gates", "id", "kind", "source", "target", "verification"},
    "standards": COMMON,
    "tools": COMMON | {"license_file", "shipped"},
    "unresolved": {"affects", "detail", "id", "owner", "title", "status", "resolution"},
    "attribution-graph": {"id", "subject", "role", "object", "status", "verification", "statement", "sources",
                          "notes", "unresolved"},
    "project-records": {"id", "path", "origin", "products", "visibility", "current_license", "decision",
                        "intended_license", "relicensing_evidence", "surviving_obligations", "traveling_notices",
                        "excluded_third_party", "lineage", "credits", "unresolved", "audited", "license",
                        "license_file", "name", "notes", "obligations", "public_ledger_note", "relationship",
                        "required_notice", "shipped", "url", "verification", "affects", "evidence"},
}  # fmt: skip
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_RE = re.compile(r"^https://[A-Za-z0-9.-]+(/[^\s]*)?$")


def norm_name(name: str) -> str:
    text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    text = re.sub(r"\(.*?\)", " ", text)
    text = re.sub(r"\b(and|&)\s+(contributors|collaborators|others|authors)\b", " ", text)
    text = re.sub(r"\b(inc|llc|ltd|pbc|corp|corporation|the)\b\.?", " ", text)
    return re.sub(r"[^a-z0-9]+", "", text)


def _check_sources(where: str, sources: Any, problems: Any, root: Path, org_root: Path | None) -> list[dict[str, Any]]:
    if not isinstance(sources, list) or not sources:
        problems.add(where, "sources must be a non-empty list")
        return []
    good = []
    for i, src in enumerate(sources):
        label = f"{where}: source {i}"
        if not isinstance(src, dict):
            problems.add(label, "must be a mapping with kind and ref")
            continue
        unknown = set(src) - {"kind", "ref", "excerpt", "checked", "title"}
        if unknown:
            problems.add(label, f"unknown source fields {sorted(unknown)}")
        kind, ref = src.get("kind"), src.get("ref")
        if kind not in SOURCE_KINDS:
            problems.add(label, f"unknown source kind {kind!r}")
        if not isinstance(ref, str) or not ref:
            problems.add(label, "ref is required")
            continue
        if ref.startswith("https://"):
            if not URL_RE.match(ref):
                problems.add(label, f"malformed URL {ref!r}")
            if not DATE_RE.match(str(src.get("checked", ""))):
                problems.add(label, "a URL source needs checked: YYYY-MM-DD")
        elif ref.startswith("credits:"):
            if not (root / ref[len("credits:"):]).exists():
                problems.add(label, f"{ref} does not exist in this repository")
        elif ref.startswith("ov:"):
            if org_root is not None:
                rel = ref[len("ov:"):].split("@", 1)[0]
                if not (org_root / rel).exists():
                    problems.add(label, f"{ref} not found under {org_root}")
        elif ref.startswith("owner:"):
            if not DATE_RE.match(ref[len("owner:"):]) or kind != "owner_declaration":
                problems.add(label, "owner refs are owner:YYYY-MM-DD with kind owner_declaration")
        elif ref.startswith("http://"):
            problems.add(label, f"use https: {ref!r}")
        else:
            problems.add(label, f"ref must be https://, credits:<path>, ov:<path> or owner:<date>, not {ref!r}")
        if isinstance(src.get("excerpt"), str) and re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", src["excerpt"]):
            problems.add(label, "excerpts must not contain e-mail addresses")
        good.append(src)
    return good


def check(root: Path, records: dict[str, tuple[str, dict[str, Any]]], sources: list[tuple[str, list[dict[str, Any]]]],
          problems: Any, org_root: Path | None) -> None:
    import yaml

    unresolved = {i: r for i, (_, r) in records.items() if i.startswith("UNR-")}
    open_unresolved = {i for i, r in unresolved.items() if r.get("status", "open") == "open"}
    for uid, rec in unresolved.items():
        if rec.get("status", "open") not in UNRESOLVED_STATUS:
            problems.add(f"provenance/unresolved.yaml:{uid}", f"status must be one of {sorted(UNRESOLVED_STATUS)}")
        if rec.get("status") == "resolved" and not rec.get("resolution"):
            problems.add(f"provenance/unresolved.yaml:{uid}", "a resolved item records its resolution")

    # I: schema drift
    for where, items in sources:
        kind = "project-records" if where.startswith("projects/") else Path(where).stem
        allowed = KNOWN_KEYS.get(kind)
        if allowed is None:
            problems.add(where, "file kind has no known schema (add it to tools/attribution.py)")
            continue
        for rec in items:
            extra = set(rec) - allowed
            if extra:
                problems.add(f"{where}:{rec.get('id') or rec.get('repo') or rec.get('asset')}",
                             f"unknown fields {sorted(extra)} (schema drift)")

    # A/B/C/F for catalog records
    for rid, (where, rec) in records.items():
        label = f"{where}:{rid}"
        if "name" in rec and not isinstance(rec["name"], str):
            problems.add(label, "name must be a string (quote YAML values that contain ': ')")
        for product in rec.get("products") or []:
            if not isinstance(product, str):
                problems.add(label, "products must be strings (quote YAML values that contain ': ')")
        for role in rec.get("roles") or []:
            if role not in ROLES:
                problems.add(label, f"unknown role {role!r}")
        if rec.get("status") is not None and not rid.startswith("UNR-") and rec["status"] not in STATUS:
            problems.add(label, f"unknown status {rec['status']!r}")
        if rec.get("roles") and "sources" not in rec and not rid.startswith("ATT-"):
            problems.add(label, "records with roles must cite sources")
        if "sources" in rec and not rid.startswith("ATT-"):
            srcs = _check_sources(label, rec["sources"], problems, root, org_root)
            ver = rec.get("verification")
            if ver == "OWNER_REPORTED" and not any(s.get("kind") == "owner_declaration" for s in srcs):
                problems.add(label, "OWNER_REPORTED needs an owner_declaration source")
        unr = rec.get("unresolved")
        unr_list = [unr] if isinstance(unr, str) else (unr or [])
        for u in set(unr_list) - open_unresolved:
            if u in unresolved:
                problems.add(label, f"links {u}, which is resolved: link an open item, or drop the link")
        if rec.get("verification") == "VERIFIED" and set(unr_list) & open_unresolved and not rec.get("verified_scope"):
            problems.add(label, "VERIFIED with an open unresolved item must state verified_scope (what is verified)")

    # The attribution graph
    graph_path = root / "provenance" / "attribution-graph.yaml"
    edges: list[dict[str, Any]] = []
    if graph_path.is_file():
        doc = yaml.safe_load(graph_path.read_text(encoding="utf-8")) or {}
        edges = doc.get("edges") or []
    by_object: dict[str, list[dict[str, Any]]] = defaultdict(list)
    pair_roles: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    referenced: set[str] = set()
    for e in edges:
        eid = e.get("id", "?")
        label = f"provenance/attribution-graph.yaml:{eid}"
        for field in ("subject", "object"):
            ref = e.get(field)
            if ref not in records:
                problems.add(label, f"{field} -> unresolved reference {ref!r}")
            referenced.add(str(ref))
        role, ver = e.get("role"), e.get("verification")
        if role not in ROLES:
            problems.add(label, f"missing or unknown role {role!r}")
        if e.get("status", "current") not in STATUS:
            problems.add(label, f"unknown status {e.get('status')!r}")
        if not e.get("statement"):
            problems.add(label, "statement (what is being credited, in words) is required")
        unr = e.get("unresolved")
        unr_list = [unr] if isinstance(unr, str) else (unr or [])
        for u in unr_list:
            if u not in unresolved:
                problems.add(label, f"unresolved -> unknown item {u!r}")
        if ver == "REVIEW_REQUIRED":
            if not unr_list:
                problems.add(label, "REVIEW_REQUIRED must link to an unresolved item")
        else:
            srcs = _check_sources(label, e.get("sources"), problems, root, org_root)
            kinds = {s.get("kind") for s in srcs}
            if ver == "OWNER_REPORTED" and "owner_declaration" not in kinds:
                problems.add(label, "OWNER_REPORTED needs an owner_declaration source")
            if role in AUTHORSHIP and kinds <= {"owner_declaration"}:
                problems.add(label, f"{role} needs an authoritative source, not only an owner declaration")
            if ver == "VERIFIED" and set(unr_list) & open_unresolved:
                problems.add(label, "VERIFIED edge links an open unresolved item")
            if role == "legal_attribution" and not kinds & {"license_file", "notice_file", "source_header"}:
                problems.add(label, "legal_attribution must cite a licence, notice or source header")
        if ver not in {"VERIFIED", "INFERRED", "OWNER_REPORTED", "REVIEW_REQUIRED"}:
            problems.add(label, f"unknown verification {ver!r}")
        by_object[str(e.get("object"))].append(e)
        pair_roles[(str(e.get("subject")), str(e.get("object")))].append(e)

    # D: no sole credit for collective work (technologies, unless their record says authorship: individual)
    for obj, es in by_object.items():
        if not obj.startswith(("tool:", "lib:", "std:", "model:")) or records.get(obj, ("", {}))[1].get("authorship") == "individual":
            continue
        individuals = [e for e in es if e.get("role") in INDIVIDUAL_CREDIT and str(e.get("subject")).startswith("person:")]
        collective = [e for e in es if e.get("role") in COLLECTIVE and not str(e.get("subject")).startswith("person:")]
        if individuals and not collective:
            problems.add(f"provenance/attribution-graph.yaml:{obj}",
                         "credits individuals but no community, host, steward or contributors (no sole credit for "
                         "collective work)")

    # E: contradictions
    for (subj, obj), es in pair_roles.items():
        roles = {e.get("role") for e in es}
        if roles & INFLUENCE and roles & CODE_LINEAGE:
            problems.add(f"provenance/attribution-graph.yaml:{subj}->{obj}",
                         f"contradictory: {sorted(roles & INFLUENCE)} and {sorted(roles & CODE_LINEAGE)}")
        seen: dict[str, str] = {}
        for e in es:
            r, s = str(e.get("role")), str(e.get("status", "current"))
            if r in seen and seen[r] != s:
                problems.add(f"provenance/attribution-graph.yaml:{subj}->{obj}",
                             f"role {r} has conflicting statuses {seen[r]} and {s}")
            seen[r] = s

    # G: duplicate identities
    names: dict[str, str] = {}
    for rid, (_where, rec) in records.items():
        if not rid.startswith(("person:", "org:", "community:")):
            continue
        for name in [rec.get("name", ""), *(rec.get("aliases") or [])]:
            key = norm_name(str(name))
            if not key:
                continue
            if key in names and names[key] != rid:
                problems.add(f"{_where}:{rid}", f"duplicate identity: {name!r} also names {names[key]}")
            names.setdefault(key, rid)

    # H: orphans
    for _where, items in sources:
        for rec in items:
            for field in ("affects", "refs", "credits", "vendor", "upstream", "source", "target", "tool", "repo"):
                vals = rec.get(field)
                referenced.update([vals] if isinstance(vals, str) else (vals or []))
    for rid, (where, rec) in records.items():
        if rid.startswith(("person:", "community:")) and rid not in referenced and not rec.get("affects"):
            problems.add(f"{where}:{rid}", "orphaned: credited for nothing (no affects and no graph edge)")

    # K: required notices are stated
    for rid, (where, rec) in records.items():
        if "REQUIRED_LICENSE_NOTICE" in (rec.get("relationship") or []) and not (
            rec.get("required_notice") or rec.get("license_file") or rec.get("license")
        ):
            problems.add(f"{where}:{rid}", "REQUIRED_LICENSE_NOTICE without required_notice, license_file or license")

    # J: history
    ledger = root / "provenance" / "id-ledger.txt"
    current = set(records)
    if not ledger.is_file():
        problems.add("provenance/id-ledger.txt", "missing (tools/validate.py --write-id-ledger)")
    else:
        issued = {line.strip() for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip() and
                  not line.startswith("#")}
        for gone in sorted(issued - current):
            problems.add("provenance/id-ledger.txt", f"{gone} was issued but no longer exists; credits are history: "
                         "mark it historical instead of deleting it")
        for new in sorted(current - issued):
            problems.add("provenance/id-ledger.txt", f"{new} is not recorded (tools/validate.py --write-id-ledger)")

    # L: human-readable view is current
    ack = root / "ACKNOWLEDGMENTS.md"
    try:
        from render_acknowledgments import render
    except ImportError:  # pragma: no cover - tools/ is always on the path when run from validate.py
        return
    if not ack.is_file() or ack.read_text(encoding="utf-8") != render(root):
        problems.add("ACKNOWLEDGMENTS.md", "stale; run tools/render_acknowledgments.py")


def write_id_ledger(root: Path, ids: set[str]) -> None:
    ledger = root / "provenance" / "id-ledger.txt"
    issued = set()
    if ledger.is_file():
        issued = {line.strip() for line in ledger.read_text(encoding="utf-8").splitlines()
                  if line.strip() and not line.startswith("#")}
    header = ("# Every credits id ever issued (append-only). tools/validate.py fails if one disappears.\n"
              "# Regenerate with tools/validate.py --write-id-ledger after adding records; never remove lines.\n")
    ledger.write_text(header + "".join(f"{i}\n" for i in sorted(issued | ids)), encoding="utf-8")
