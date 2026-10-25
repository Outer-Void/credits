"""Regression tests for the comprehensive-attribution checks (tools/attribution.py) and the data they protect."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import validate  # noqa: E402

GRAPH = "provenance/attribution-graph.yaml"


def load(rel: str) -> dict:  # type: ignore[type-arg]
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def edges() -> list[dict]:  # type: ignore[type-arg]
    return load(GRAPH)["edges"]


class AttributionChecks(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "credits"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def edit(self, rel: str, fn) -> None:  # type: ignore[no-untyped-def]
        path = self.root / rel
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        fn(doc)
        path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")

    def add_edge(self, **edge) -> None:  # type: ignore[no-untyped-def]
        base = {"id": "ATT-999", "status": "current", "verification": "VERIFIED", "statement": "test",
                "sources": [{"kind": "documentation", "ref": "https://example.org/x", "checked": "2026-10-25"}]}
        self.edit(GRAPH, lambda d: d["edges"].append({**base, **edge}))

    def caught(self, needle: str, ignore_ledger: bool = True) -> None:
        probs = [p for p in validate.validate(self.root) if not (ignore_ledger and "id-ledger" in p and "ATT-999" in p)]
        self.assertTrue(any(needle in p for p in probs), f"{needle!r} not in {probs}")

    def test_unknown_role(self) -> None:
        self.add_edge(subject="person:guido-van-rossum", role="godfather", object="tool:python")
        self.caught("unknown role 'godfather'")

    def test_edge_needs_sources(self) -> None:
        self.add_edge(subject="person:guido-van-rossum", role="maintainer", object="tool:python", sources=[])
        self.caught("sources must be a non-empty list")

    def test_authorship_needs_an_authoritative_source(self) -> None:
        self.add_edge(subject="person:jadis", role="creator", object="tool:python", verification="OWNER_REPORTED",
                      sources=[{"kind": "owner_declaration", "ref": "owner:2026-10-25"}])
        self.caught("creator needs an authoritative source")

    def test_owner_reported_needs_an_owner_declaration(self) -> None:
        self.add_edge(subject="ai:chatgpt", role="ai_assistance", object="org:outer-void", verification="OWNER_REPORTED")
        self.caught("OWNER_REPORTED needs an owner_declaration source")

    def test_no_sole_credit_for_collective_work(self) -> None:
        def drop(d):  # type: ignore[no-untyped-def]
            d["edges"] = [e for e in d["edges"] if not (e["object"] == "tool:python" and e["subject"] != "person:guido-van-rossum")]
        self.edit(GRAPH, drop)
        self.caught("no sole credit for collective work")

    def test_inspiration_and_code_lineage_contradict(self) -> None:
        self.add_edge(subject="proj:hermes-agent", role="inspiration", object="repo:blhermes-agent")
        self.caught("contradictory")

    def test_conflicting_status(self) -> None:
        self.add_edge(subject="person:linus-torvalds", role="maintainer", object="tool:linux", status="historical")
        self.caught("conflicting statuses")

    def test_unresolved_shown_as_verified(self) -> None:
        def unscope(d):  # type: ignore[no-untyped-def]
            for r in d["assets"]:
                r.pop("verified_scope", None)
        self.edit("catalog/assets.yaml", unscope)
        self.caught("must state verified_scope")

    def test_records_cannot_link_resolved_items(self) -> None:
        def relink(d):  # type: ignore[no-untyped-def]
            for r in d["libraries"]:
                if r["id"] == "lib:pypi/bandit":
                    r["unresolved"] = "UNR-013"
        self.edit("catalog/libraries.yaml", relink)
        self.caught("links UNR-013, which is resolved")

    def test_duplicate_identity(self) -> None:
        self.edit("catalog/people.yaml", lambda d: d["people"].append(
            {"id": "person:guido-2", "name": "Guido van Rossum", "relationship": ["COMMUNITY"], "affects": ["tool:python"]}))
        self.caught("duplicate identity")

    def test_orphaned_person(self) -> None:
        self.edit("catalog/people.yaml", lambda d: d["people"].append(
            {"id": "person:nobody-in-particular", "name": "Nobody In Particular", "relationship": ["COMMUNITY"]}))
        self.caught("orphaned")

    def test_schema_drift(self) -> None:
        self.edit("catalog/tools.yaml", lambda d: d["tools"][0].__setitem__("popularity", 10))
        self.caught("schema drift")

    def test_deleting_a_credit_is_caught(self) -> None:
        self.edit("catalog/people.yaml", lambda d: d["people"].__setitem__(
            slice(None), [p for p in d["people"] if p["id"] != "person:tavmjong-bah"]))
        self.caught("person:tavmjong-bah was issued but no longer exists")

    def test_new_ids_must_be_recorded(self) -> None:
        self.edit("catalog/communities.yaml", lambda d: d["communities"].append(
            {"id": "community:new-one", "name": "New One", "relationship": ["COMMUNITY"], "affects": ["tool:python"]}))
        self.caught("community:new-one is not recorded")

    def test_legal_attribution_cites_a_licence(self) -> None:
        self.add_edge(subject="proj:hermes-agent", role="legal_attribution", object="repo:blux")
        self.caught("legal_attribution must cite a licence")

    def test_bad_sources(self) -> None:
        self.add_edge(subject="person:guido-van-rossum", role="maintainer", object="tool:python", sources=[
            {"kind": "documentation", "ref": "http://example.org"},
            {"kind": "documentation", "ref": "https://example.org/a", "checked": "2026-10-25", "excerpt": "mail jo@example.org"},
            {"kind": "rumour", "ref": "credits:does-not-exist.md"}])
        for needle in ("use https", "must not contain e-mail", "unknown source kind 'rumour'", "does not exist"):
            self.caught(needle)

    def test_names_must_be_strings(self) -> None:
        self.edit("projects/blux-coga.yaml", lambda d: d["project"].__setitem__("products", [{"BLUX CogA (2.0": "x"}]))
        self.caught("products must be strings")

    def test_stale_acknowledgments(self) -> None:
        (self.root / "ACKNOWLEDGMENTS.md").write_text("# stale\n", encoding="utf-8")
        self.caught("ACKNOWLEDGMENTS.md")

    def test_acknowledgments_are_current(self) -> None:
        proc = subprocess.run([sys.executable, str(ROOT / "tools" / "render_acknowledgments.py"), "--check"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)


class ProtectedAttributions(unittest.TestCase):
    """Established attributions that must not silently disappear or change meaning."""

    def has(self, subject: str, role: str, obj: str) -> bool:
        return any(e["subject"] == subject and e["role"] == role and e["object"] == obj for e in edges())

    def test_core_lineage(self) -> None:
        for subject, role, obj in (
            ("person:guido-van-rossum", "creator", "tool:python"), ("org:psf", "steward", "tool:python"),
            ("person:linus-torvalds", "creator", "tool:linux"), ("person:linus-torvalds", "developer", "tool:git"),
            ("person:richard-stallman", "founder", "tool:gnu"), ("person:brian-fox", "original_author", "tool:bash"),
            ("person:chet-ramey", "maintainer", "tool:bash"), ("person:ian-murdock", "founder", "tool:debian"),
            ("person:cedric-vincent", "original_author", "tool:proot"), ("org:jetbrains", "developer", "tool:kotlin"),
        ):
            self.assertTrue(self.has(subject, role, obj), (subject, role, obj))

    def test_hermes_lineage_and_notices(self) -> None:
        self.assertTrue(self.has("proj:hermes-agent", "fork_origin", "repo:blhermes-agent"))
        self.assertTrue(self.has("org:nous-research", "copyright_holder", "proj:hermes-agent"))
        self.assertTrue(self.has("proj:hermes-agent", "legal_attribution", "repo:blhermes-agent"))
        nested = [e for e in edges() if e["role"] == "legal_attribution" and e["subject"].startswith("proj:hermes-nested/")]
        self.assertEqual(len(nested), 18)
        lineage = load("provenance/source-lineage.yaml")["lineage"]
        self.assertIn("LIN-001", {r["id"] for r in lineage})
        # BLUX credits Hermes as influence, never as code lineage (no Hermes code is in BLUX).
        blux = {e["role"] for e in edges() if e["subject"] == "proj:hermes-agent" and e["object"] == "repo:blux"}
        self.assertEqual(blux, {"architectural_influence"})

    def test_owner_reported_ai(self) -> None:
        ai = {r["id"]: r for r in load("catalog/ai.yaml")["ai"]}
        for rid in ("ai:chatgpt", "ai:deepseek-dev", "ai:blackbox-dev", "ai:meta-llama"):
            self.assertEqual(ai[rid]["verification"], "OWNER_REPORTED")
            self.assertEqual(ai[rid]["sources"][0]["kind"], "owner_declaration")
        self.assertEqual(ai["ai:claude-code"]["verification"], "VERIFIED")

    def test_unverified_originators_stay_unresolved(self) -> None:
        unr = {u["id"]: u for u in load("provenance/unresolved.yaml")["unresolved"]}
        self.assertEqual(unr["UNR-017"]["status"], "open")
        names = {p["name"] for p in load("catalog/people.yaml")["people"]}
        for unverified in ("Fredrik Fornwall", "Andrey Breslav", "Ryan Dahl", "Jordan Walke"):
            self.assertNotIn(unverified, names, "not verified from an authoritative source yet (UNR-017)")


if __name__ == "__main__":
    unittest.main()
