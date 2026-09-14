#!/usr/bin/env python3
# =============================================================================
# test_ingestion.py — Self-test M2 for AC-001..AC-005 (isolated, deterministic)
# Asisten Pengetahuan Internal Toko Makmur Jaya
# Architecture version: 1.2 (Flow A) | Matrix 1.0
# =============================================================================
# Run:  python tests/harness/test_ingestion.py
# Exit: 0 = all passed, 1 = failures. Stdlib only.
#
# Coverage:
#   AC-001 valid corpus                     -> active, doc_count=26, metadata ok
#   AC-002 invalid corpus (hidden/edge)     -> rejected, previous active preserved
#   AC-003 duplicate/concurrent rerun       -> no-op, single active, no dup chunks
#   AC-004 embedding timeout                -> candidate failed, old active kept
#   AC-005 provider/database failure        -> auth/5xx/dim/db fail, no activation
# =============================================================================

import hashlib
import os
import sys
import threading
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mocks", "ai-provider"))

import rag_ingest_core as core
from provider_mock import deterministic_embedding, serve

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS_DIR = os.path.join(BASE, "docs")
FIXTURE_CORPUS = os.path.join(BASE, "tests", "fixtures", "corpus", "synthetic_corpus.md")


# --------------------------------------------------------------------------
# corpus loading helpers
# --------------------------------------------------------------------------
def load_docs() -> dict:
    """Load the 26 official docs/ files as {relpath: bytes}."""
    files = {}
    for name in sorted(os.listdir(CORPUS_DIR)):
        if name.endswith(".md"):
            with open(os.path.join(CORPUS_DIR, name), "rb") as fh:
                files[name] = fh.read()
    return files


def tiny_files(n: int = 2) -> dict:
    """Small synthetic corpus for fast tests."""
    return {
        "00_Company_Profile_Toko_Makmur_Jaya.md": b"# Profil\n\nToko Makmur Jaya.\n",
        "01_SOP_Buka_Toko.md": b"# SOP Buka Toko\n\nBuka 08:00.\n",
    }


def local_embed(texts, timeout_ms=2000):
    """In-process deterministic embedding (no network)."""
    return [deterministic_embedding(t, 384) for t in texts]


CONFIG = core.RAGConfig()


class HttpMockMixin:
    """Start provider_mock server on ephemeral port for fault-injection tests."""

    @classmethod
    def setUpClass(cls):
        cls.mock_port = 18080 + (os.getpid() % 5000)
        cls.server_thread = threading.Thread(
            target=serve, args=(cls.mock_port, "127.0.0.1"), daemon=True
        )
        cls.server_thread.start()
        time.sleep(0.3)

    def embed_http(self, base_url):
        return core.http_embed_fn(base_url, CONFIG.embedding_model, CONFIG.embed_timeout_ms)

    def mock_base(self):
        return f"http://127.0.0.1:{self.mock_port}"


# --------------------------------------------------------------------------
# AC-001 — valid corpus
# --------------------------------------------------------------------------
class TestAC001Valid(HttpMockMixin, unittest.TestCase):
    def test_26_documents_activate(self):
        store = core.Store()
        files = load_docs()
        self.assertEqual(len(files), 26, "baseline corpus must have 26 docs")

        result = core.run_ingestion(store, files, CONFIG, local_embed)
        self.assertEqual(result["status"], "active")
        self.assertEqual(result["document_count"], 26)
        self.assertGreater(result["chunk_count"], 0)

        # only this version queryable; all chunks have required metadata
        active = store.settings["active_corpus_version"]
        self.assertEqual(active, result["corpus_version"])
        query = store.query_active()
        self.assertEqual(len(query), result["chunk_count"])
        required = {"source_name", "source_hash", "chunk_index", "corpus_version", "embedding_profile_id"}
        for rec in query:
            self.assertTrue(required.issubset(set(rec["metadata"].keys())),
                            f"missing metadata: {required - set(rec['metadata'])}")
        # every chunk embedding profile == active profile
        self.assertEqual(store.settings["embedding_profile_id"], CONFIG.profile_id())

    def test_manifest_is_content_hash(self):
        store = core.Store()
        files = load_docs()
        result = core.run_ingestion(store, files, CONFIG, local_embed)
        manifest_hash, entries = core.build_manifest(files)
        self.assertEqual(result["corpus_version"], manifest_hash)

    def test_http_embedding_path_ok(self):
        # also verify the HTTP adapter path (used in fault tests) works end-to-end
        store = core.Store()
        files = tiny_files()
        result = core.run_ingestion(store, files, CONFIG, self.embed_http(self.mock_base()))
        self.assertEqual(result["status"], "active")
        self.assertEqual(result["document_count"], 2)


# --------------------------------------------------------------------------
# AC-002 — invalid corpus rejected; previous active preserved
# --------------------------------------------------------------------------
class TestAC002Invalid(unittest.TestCase):
    def test_empty_file_rejected(self):
        store = core.Store()
        core.run_ingestion(store, tiny_files(), CONFIG, local_embed)
        before = store.settings["active_corpus_version"]

        bad = tiny_files()
        bad["02_SOP_Tutup_Toko.md"] = b""   # empty file
        result = core.run_ingestion(store, bad, CONFIG, local_embed)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error_category"], "ValidationFailure")
        self.assertEqual(store.settings["active_corpus_version"], before,
                         "previous active must be preserved after failed candidate")

    def test_non_markdown_rejected(self):
        store = core.Store()
        core.run_ingestion(store, tiny_files(), CONFIG, local_embed)
        before = store.settings["active_corpus_version"]

        bad = tiny_files()
        bad["notes.txt"] = b"hello"          # unsupported extension
        result = core.run_ingestion(store, bad, CONFIG, local_embed)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error_category"], "ValidationFailure")
        self.assertEqual(store.settings["active_corpus_version"], before)

    def test_path_traversal_rejected(self):
        store = core.Store()
        core.run_ingestion(store, tiny_files(), CONFIG, local_embed)
        before = store.settings["active_corpus_version"]

        bad = tiny_files()
        bad["../outside.md"] = b"# outside"  # traversal
        result = core.run_ingestion(store, bad, CONFIG, local_embed)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error_category"], "ValidationFailure")
        self.assertEqual(store.settings["active_corpus_version"], before)

    def test_absolute_path_rejected(self):
        store = core.Store()
        core.run_ingestion(store, tiny_files(), CONFIG, local_embed)
        before = store.settings["active_corpus_version"]

        bad = tiny_files()
        bad["/etc/passwd.md"] = b"# x"
        result = core.run_ingestion(store, bad, CONFIG, local_embed)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(store.settings["active_corpus_version"], before)

    def test_bad_filename_rejected(self):
        store = core.Store()
        core.run_ingestion(store, tiny_files(), CONFIG, local_embed)
        before = store.settings["active_corpus_version"]

        bad = tiny_files()
        bad["sop_toha.md"] = b"# x"           # does not match NN_ prefix
        result = core.run_ingestion(store, bad, CONFIG, local_embed)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(store.settings["active_corpus_version"], before)

    def test_no_partial_corpus_visible_to_qa(self):
        # invalid candidate must never become queryable
        store = core.Store()
        core.run_ingestion(store, tiny_files(), CONFIG, local_embed)
        before = store.settings["active_corpus_version"]

        bad = tiny_files()
        bad["02_SOP_Tutup_Toko.md"] = b""
        core.run_ingestion(store, bad, CONFIG, local_embed)

        query = store.query_active()
        for rec in query:
            self.assertNotEqual(rec["corpus_version"], bad.get("corpus_version", None))
        self.assertNotEqual(store.settings["active_corpus_version"], None)
        # exactly one active version
        active_versions = [v for v, r in store.versions.items() if r["status"] == "active"]
        self.assertEqual(len(active_versions), 1)


# --------------------------------------------------------------------------
# AC-003 — duplicate manifest / concurrent rerun -> no-op
# --------------------------------------------------------------------------
class TestAC003Duplicate(unittest.TestCase):
    def test_identical_rerun_is_noop(self):
        store = core.Store()
        files = load_docs()
        first = core.run_ingestion(store, files, CONFIG, local_embed)
        chunks_before = store.versions[first["corpus_version"]]["chunk_count"]

        second = core.run_ingestion(store, files, CONFIG, local_embed)

        self.assertEqual(second["status"], "duplicate")
        self.assertEqual(second["corpus_version"], first["corpus_version"])
        # no new chunks
        self.assertEqual(store.versions[first["corpus_version"]]["chunk_count"], chunks_before)
        # still exactly one active version
        active_versions = [v for v, r in store.versions.items() if r["status"] == "active"]
        self.assertEqual(len(active_versions), 1)

    def test_near_simultaneous_reruns_single_active(self):
        store = core.Store()
        files = tiny_files()
        results = []
        results_guard = threading.Lock()

        def run():
            r = core.run_ingestion(store, files, CONFIG, local_embed)
            with results_guard:
                results.append(r)

        threads = [threading.Thread(target=run) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        statuses = [r["status"] for r in results]
        versions = {r["corpus_version"] for r in results if r["status"] != "failed"}
        self.assertEqual(len(versions), 1, "all successful runs must share one corpus identity")
        self.assertIn("duplicate", statuses, "near-simultaneous reruns must be no-op duplicates")
        active_versions = [v for v, r in store.versions.items() if r["status"] == "active"]
        self.assertEqual(len(active_versions), 1, "exactly one active version")

    def test_changed_content_new_version_old_superseded(self):
        store = core.Store()
        files = tiny_files()
        first = core.run_ingestion(store, files, CONFIG, local_embed)

        changed = dict(files)
        changed["01_SOP_Buka_Toko.md"] = b"# SOP Buka Toko\n\nBuka 09:00.\n"  # content change
        second = core.run_ingestion(store, changed, CONFIG, local_embed)

        self.assertEqual(second["status"], "active")
        self.assertNotEqual(second["corpus_version"], first["corpus_version"])
        self.assertEqual(store.settings["active_corpus_version"], second["corpus_version"])
        # old version is superseded, not active
        self.assertEqual(store.versions[first["corpus_version"]]["status"], "superseded")
        # Q&A query only sees new version chunks
        query = store.query_active()
        for rec in query:
            self.assertEqual(rec["corpus_version"], second["corpus_version"])


# --------------------------------------------------------------------------
# AC-004 — embedding timeout -> candidate failed, old active kept
# --------------------------------------------------------------------------
class TestAC004Timeout(HttpMockMixin, unittest.TestCase):
    def test_timeout_fails_candidate_keeps_old(self):
        store = core.Store()
        files = tiny_files()
        ok = core.run_ingestion(store, files, CONFIG, local_embed)
        self.assertEqual(ok["status"], "active")
        before = store.settings["active_corpus_version"]

        # inject delay > timeout so embedding call stalls
        os.environ["MOCK_EMBED_DELAY_MS"] = "5000"
        try:
            changed = dict(files)
            changed["01_SOP_Buka_Toko.md"] = b"# SOP Buka Toko\n\nBuka 10:00.\n"
            result = core.run_ingestion(store, changed, CONFIG,
                                        self.embed_http(self.mock_base()))
        finally:
            os.environ.pop("MOCK_EMBED_DELAY_MS", None)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error_category"], "TimeoutFailure")
        self.assertEqual(store.settings["active_corpus_version"], before,
                         "old active version untouched after timeout")

    def test_timeout_safe_event_recorded(self):
        store = core.Store()
        core.run_ingestion(store, tiny_files(), CONFIG, local_embed)
        os.environ["MOCK_EMBED_DELAY_MS"] = "5000"
        try:
            changed = dict(tiny_files())
            changed["01_SOP_Buka_Toko.md"] = b"# changed"
            core.run_ingestion(store, changed, CONFIG, self.embed_http(self.mock_base()))
        finally:
            os.environ.pop("MOCK_EMBED_DELAY_MS", None)

        failed_events = [e for e in store.safe_events if e["status"] == "failed"]
        self.assertTrue(failed_events)
        self.assertEqual(failed_events[-1]["error_category"], "TimeoutFailure")


# --------------------------------------------------------------------------
# AC-005 — provider/database failure (auth, 5xx, wrong dim, db fail)
# --------------------------------------------------------------------------
class TestAC005ProviderFailure(HttpMockMixin, unittest.TestCase):
    def test_auth_401_fails_candidate(self):
        store = core.Store()
        files = tiny_files()
        ok = core.run_ingestion(store, files, CONFIG, local_embed)
        before = store.settings["active_corpus_version"]

        os.environ["MOCK_EMBED_STATUS"] = "401"
        try:
            changed = dict(files)
            changed["01_SOP_Buka_Toko.md"] = b"# changed 401"
            result = core.run_ingestion(store, changed, CONFIG,
                                        self.embed_http(self.mock_base()))
        finally:
            os.environ.pop("MOCK_EMBED_STATUS", None)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error_category"], "ProviderFailure")
        self.assertEqual(store.settings["active_corpus_version"], before)

    def test_all_5xx_statuses_fail_candidate(self):
        for status in (500, 502, 503):
            store = core.Store()
            files = tiny_files()
            core.run_ingestion(store, files, CONFIG, local_embed)
            before = store.settings["active_corpus_version"]

            os.environ["MOCK_EMBED_STATUS"] = str(status)
            try:
                changed = dict(files)
                changed["01_SOP_Buka_Toko.md"] = b"# changed 5xx"
                result = core.run_ingestion(store, changed, CONFIG,
                                            self.embed_http(self.mock_base()))
            finally:
                os.environ.pop("MOCK_EMBED_STATUS", None)

            self.assertEqual(result["status"], "failed", f"status {status}")
            self.assertEqual(result["error_category"], "ProviderFailure")
            self.assertEqual(store.settings["active_corpus_version"], before)

    def test_dimension_mismatch_fails_candidate(self):
        store = core.Store()
        files = tiny_files()
        core.run_ingestion(store, files, CONFIG, local_embed)
        before = store.settings["active_corpus_version"]

        # provider returns wrong dimension for this request (dim differs from CONFIG 384)
        os.environ["MOCK_EMBEDDING_DIM"] = "512"
        try:
            changed = dict(files)
            changed["01_SOP_Buka_Toko.md"] = b"# changed dim"
            # use local_embed with forced dimension via direct closure
            def wrong_dim_embed(texts, timeout_ms=2000):
                return [deterministic_embedding(t, 512) for t in texts]
            result = core.run_ingestion(store, changed, CONFIG, wrong_dim_embed)
        finally:
            os.environ.pop("MOCK_EMBEDDING_DIM", None)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error_category"], "ValidationFailure")
        self.assertEqual(store.settings["active_corpus_version"], before)

    def test_database_write_failure(self):
        store = core.FailingStore()
        files = tiny_files()
        result = core.run_ingestion(store, files, CONFIG, local_embed)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error_category"], "DatabaseFailure")
        # no activation happened
        self.assertIsNone(store.settings["active_corpus_version"])

    def test_no_activation_on_failure(self):
        store = core.Store()
        core.run_ingestion(store, tiny_files(), CONFIG, local_embed)
        before = store.settings["active_corpus_version"]

        os.environ["MOCK_EMBED_STATUS"] = "500"
        try:
            changed = dict(tiny_files())
            changed["01_SOP_Buka_Toko.md"] = b"# noc"
            core.run_ingestion(store, changed, CONFIG, self.embed_http(self.mock_base()))
        finally:
            os.environ.pop("MOCK_EMBED_STATUS", None)

        self.assertEqual(store.settings["active_corpus_version"], before)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)