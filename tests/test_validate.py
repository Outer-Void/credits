"""Validator tests: the real ledger passes; each class of defect is caught."""

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


class LedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "credits"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def edit(self, rel: str, fn) -> None:  # type: ignore[no-untyped-def]
        path = self.root / rel
        doc = yaml.safe_load(path.read_text())
        fn(doc)
        path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True))

    def problems(self) -> list[str]:
        return list(validate.validate(self.root))

    def assertCaught(self, needle: str) -> None:
        probs = self.problems()
        self.assertTrue(any(needle in p for p in probs), f"{needle!r} not in {probs}")

    def test_real_ledger_is_valid(self) -> None:
        self.assertEqual(validate.validate(ROOT), [])

    def test_unresolved_report_is_current(self) -> None:
        proc = subprocess.run([sys.executable, str(ROOT / "tools" / "render_unresolved.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_dangling_reference(self) -> None:
        self.edit("catalog/inspirations.yaml", lambda d: d["inspirations"][0]["affects"].append("repo:nope"))
        self.assertCaught("unresolved reference 'repo:nope'")

    def test_missing_decision(self) -> None:
        self.edit("projects/void-os.yaml", lambda d: d["project"].__setitem__("decision", "WHATEVER"))
        self.assertCaught("decision 'WHATEVER'")

    def test_missing_project_record(self) -> None:
        (self.root / "projects" / "lrc.yaml").unlink()
        self.assertCaught("repo:lrc has no projects/ record")

    def test_deleted_license_text(self) -> None:
        (self.root / "licenses" / "OFL-1.1.txt").unlink()
        self.assertCaught("licence texts were added, removed or changed")
        self.assertCaught("license_file missing: licenses/OFL-1.1.txt")

    def test_altered_license_text(self) -> None:
        p = self.root / "licenses" / "Apache-2.0.txt"
        p.write_text(p.read_text().replace("Apache", "Apathy", 1))
        self.assertCaught("licence texts were added, removed or changed")

    def test_review_required_without_unresolved(self) -> None:
        def strip(d):  # type: ignore[no-untyped-def]
            for a in d["assets"]:
                if a["license"] == "UNKNOWN":
                    a.pop("unresolved")
                    break

        self.edit("catalog/assets.yaml", strip)
        self.assertCaught("must link to an unresolved item")

    def test_unresolved_item_must_be_visible(self) -> None:
        self.edit("provenance/unresolved.yaml", lambda d: d["unresolved"].append({"id": "UNR-999", "title": "t", "affects": [], "owner": "x", "detail": "d"}))
        self.assertCaught("UNR-999 is not listed")

    def test_lineage_must_be_listed_by_target(self) -> None:
        self.edit("projects/blhermes-agent.yaml", lambda d: d["project"].__setitem__("lineage", []))
        self.assertCaught("LIN-001: target repo:blhermes-agent does not list this lineage")

    def test_fork_without_lineage(self) -> None:
        self.edit("provenance/source-lineage.yaml", lambda d: d["lineage"].pop(0))
        self.assertCaught("fork/derivative source without a lineage record")

    def test_bad_relationship_class(self) -> None:
        self.edit("catalog/tools.yaml", lambda d: d["tools"][0]["relationship"].append("FRIEND"))
        self.assertCaught("unknown relationship class FRIEND")

    def test_duplicate_id(self) -> None:
        self.edit("catalog/standards.yaml", lambda d: d["standards"].append(dict(d["standards"][0])))
        self.assertCaught("duplicate id std:json-schema-2020-12")

    def test_traveling_notice_checked_in_checkout(self) -> None:
        org = self.tmp / "org"
        (org / "voidforge").mkdir(parents=True)
        (org / "voidforge" / "LICENSE").write_text("x")
        probs = validate.validate(self.root, org_root=org)
        self.assertTrue(any("voidforge" in p and "THIRD_PARTY_NOTICES" in p for p in probs), probs)


class SpdxTests(unittest.TestCase):
    def test_valid(self) -> None:
        for expr in ["MIT", "Apache-2.0", "MIT AND Bitstream-Vera", "(MIT OR Apache-2.0) AND OFL-1.1",
                     "GPL-2.0-only WITH Classpath-exception-2.0", "LicenseRef-OuterVoid-Proprietary", "UNKNOWN", "NOASSERTION", "Apache-2.0+"]:  # fmt: skip
            self.assertIsNone(validate.check_spdx(expr), expr)

    def test_invalid(self) -> None:
        for expr in ["MIT License", "Apache 2", "MIT AND", "(MIT", "MIT OR OR Apache-2.0", "GPL-2.0-only WITH Foo", "", "mit", "GPL-2.0+"]:
            self.assertIsNotNone(validate.check_spdx(expr), expr)


if __name__ == "__main__":
    unittest.main()
