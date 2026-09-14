#!/usr/bin/env python3
# =============================================================================
# rag_ingest_core.py — contract-level ingestion core (MIRROR of workflow 01)
# Asisten Pengetahuan Internal Toko Makmur Jaya
# Architecture version: 1.2 (Flow A) | AC-001..AC-005
# =============================================================================
# STATUS: This module is a TEST HARNESS implementation of the ingestion
# contract that workflow `workflows/01-corpus-ingestion.json` implements with
# built-in n8n nodes (Read Binary Files -> Code -> HTTP Request -> Postgres).
#
# It is NOT shipped runtime code. Runtime = n8n + PostgreSQL/pgvector on VPS.
# The harness proves the contract logic deterministically on a synthetic
# in-process store mirroring the `rag` schema (staging/active pointer/rollback).
#
# Invariants implemented (from architecture Flow A):
#   - only regular .md files at corpus root; reject traversal/symlink-out/
#     empty files/other extensions/unreadable files BEFORE activation
#   - canonical manifest: sorted relative paths + content hash; manifest hash
#     becomes corpus_version
#   - chunk metadata minimum: source_name, source_hash, chunk_index,
#     corpus_version, embedding_profile_id
#   - single embedding profile for index+query; profile guard
#   - staging writes; ONLY after full validation -> atomic activation
#   - failure -> candidate failed, active version preserved (rollback = pointer)
#   - identical manifest rerun = no-op (duplicate), no duplicate chunks
# =============================================================================

import hashlib
import json
import re
import socket
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


# --------------------------------------------------------------------------
# error taxonomy (safe categories recorded in safe_events)
# --------------------------------------------------------------------------
class TimeoutFailure(Exception):
    """Embedding/chat call exceeded internal budget."""


class ProviderFailure(Exception):
    """Auth rejection, HTTP 5xx, malformed/unsupported provider response."""


class ValidationFailure(Exception):
    """Corpus, metadata, dimension, or embedding-profile guard failure."""


class DatabaseFailure(Exception):
    """Staging/write/activation database error."""


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def embedding_profile_id(model: str, normalization: str, dimension: int) -> str:
    """Deterministic embedding profile identity (ADR-002)."""
    return hashlib.sha256(f"{model}|{normalization}|{dimension}".encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------
# RAG configuration (frozen per run; values calibrated by Engineer)
# --------------------------------------------------------------------------
@dataclass
class RAGConfig:
    config_revision: str = "2026-09-14-m2-provisional"
    chunk_size: int = 800          # provisional until calibration vs eval set
    chunk_overlap: int = 80        # provisional until calibration vs eval set
    embedding_model: str = "mock-embedding-model-v1"
    normalization: str = "l2"
    embedding_dimension: int = 384
    embed_timeout_ms: int = 2000
    retrieval_limit: int = 5
    minimum_similarity: float = 0.75
    context_bound: int = 3000
    output_bound: int = 500

    def profile_id(self) -> str:
        return embedding_profile_id(self.embedding_model, self.normalization, self.embedding_dimension)


# --------------------------------------------------------------------------
# In-process store: stand-in for `rag` schema (contract level)
# --------------------------------------------------------------------------
class Store:
    """
    Mirrors rag.corpus_versions / rag.documents / rag.settings / rag.safe_events
    with single-lock transactional activation (atomic pointer swap).
    """

    def __init__(self):
        self._lock = threading.RLock()
        self.versions = {}          # corpus_version -> record dict
        self.documents = {}         # (version, source_hash, chunk_index) -> record
        self.settings = {
            "active_corpus_version": None,
            "embedding_profile_id": None,
            "config_revision": "UNINITIALIZED",
        }
        self.safe_events = []       # sanitized events only (no payload)

    # -- writes (staging) ----------------------------------------------------
    def prepare_staging(self, version: str, profile_id: str, config_revision: str):
        """Reset any identical staging (idempotent rebuild). Raises DatabaseFailure."""
        with self._lock:
            try:
                self.versions.pop(version, None)
                for key in [k for k in self.documents if k[0] == version]:
                    self.documents.pop(key, None)
                self.versions[version] = {
                    "status": "staging",
                    "document_count": 0,
                    "chunk_count": 0,
                    "embedding_profile_id": profile_id,
                    "created_at": time.time(),
                    "activated_at": None,
                    "failed_at": None,
                    "failure_reason": None,
                }
            except Exception as exc:  # pragma: no cover - defensive
                raise DatabaseFailure(f"staging prepare failed: {exc}")

    def write_staging_document(self, version, source_hash, chunk_index, content, embedding, metadata):
        with self._lock:
            key = (version, source_hash, chunk_index)
            if key in self.documents:
                raise DatabaseFailure("duplicate chunk identity during staging")
            self.documents[key] = {
                "content": content,
                "embedding": embedding,
                "metadata": metadata,
            }
            self.versions[version]["chunk_count"] += 1

    def finish_staging_document(self, version):
        self.versions[version]["document_count"] += 1

    def mark_failed(self, version, reason, category):
        with self._lock:
            if version in self.versions:
                self.versions[version]["status"] = "failed"
                self.versions[version]["failed_at"] = time.time()
                self.versions[version]["failure_reason"] = reason
            self.record_safe_event(correlation_id="ingest", workflow="ingestion",
                                   stage="candidate", status="failed",
                                   duration_ms=0, error_category=category,
                                   config_revision=self.settings["config_revision"],
                                   corpus_version=version)

    # -- atomic activation ----------------------------------------------------
    def activate(self, version: str, profile_id: str, config_revision: str):
        """Single-lock transaction: pointer swap, old active becomes superseded."""
        with self._lock:
            if version not in self.versions:
                raise DatabaseFailure(f"candidate version {version} not in staging")
            if self.versions[version]["status"] != "staging":
                raise DatabaseFailure("activation requires staging status")
            if self.versions[version]["embedding_profile_id"] != profile_id:
                raise ValidationFailure("embedding profile mismatch at activation")
            current = self.settings["active_corpus_version"]
            if current and current in self.versions:
                self.versions[current]["status"] = "superseded"
            self.versions[version]["status"] = "active"
            self.versions[version]["activated_at"] = time.time()
            self.settings["active_corpus_version"] = version
            self.settings["embedding_profile_id"] = profile_id
            self.settings["config_revision"] = config_revision

    def rollback_active(self, to_version: str):
        """Rollback = point active pointer back to a complete earlier version."""
        with self._lock:
            if to_version not in self.versions:
                raise DatabaseFailure(f"rollback target {to_version} not found")
            current = self.settings["active_corpus_version"]
            if current and current in self.versions:
                self.versions[current]["status"] = "superseded"
            self.versions[to_version]["status"] = "active"
            self.settings["active_corpus_version"] = to_version

    def query_active(self, version=None):
        """Only active corpus version is queryable (contract for Q&A later)."""
        with self._lock:
            active = version or self.settings["active_corpus_version"]
            if not active:
                return []
            return [
                {"corpus_version": v, "source_name": rec["metadata"].get("source_name"),
                 "source_hash": h, "chunk_index": i, "content": rec["content"],
                 "embedding": rec["embedding"], "metadata": rec["metadata"]}
                for (v, h, i), rec in self.documents.items() if v == active
            ]

    def record_safe_event(self, correlation_id, workflow, stage, status,
                          duration_ms, error_category, config_revision, corpus_version):
        self.safe_events.append({
            "correlation_id": correlation_id,
            "workflow": workflow,
            "stage": stage,
            "status": status,
            "duration_ms": duration_ms,
            "error_category": error_category,
            "config_revision": config_revision,
            "corpus_version": corpus_version,
        })


class FailingStore(Store):
    """Fault injection: database write failure during staging."""

    def __init__(self, fail_on="staging"):
        super().__init__()
        self.fail_on = fail_on

    def write_staging_document(self, *args, **kwargs):
        raise DatabaseFailure(f"injected db error at {self.fail_on}")


# --------------------------------------------------------------------------
# corpus validation (Flow A step 2)
# --------------------------------------------------------------------------
MD_RE = re.compile(r"^[0-9]{2}_.+\.md$")


def validate_corpus(files: dict) -> list:
    """
    files: {relative_posix_path: bytes}
    Returns list of human-safe rejection reasons (empty == valid).
    Rejects: non-.md, empty content, undecodable content, traversal/absolute path.
    (Real symlink-out-of-mount check: read-only mount + N8N_RESTRICT_FILE_ACCESS_TO
    + workflow validation; harness simulates path-level escape.)
    """
    errors = []
    for relpath in sorted(files.keys()):
        if relpath.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", relpath):
            errors.append(f"absolute path not allowed: {relpath}")
            continue
        parts = relpath.split("/")
        if ".." in parts or "\\" in relpath:
            errors.append(f"path traversal not allowed: {relpath}")
            continue
        if not relpath.endswith(".md"):
            errors.append(f"non-markdown file rejected: {relpath}")
            continue
        if not MD_RE.match(relpath):
            errors.append(f"unexpected corpus file name (want NN_*.md): {relpath}")
            continue
        content = files[relpath]
        if not content or not content.strip():
            errors.append(f"empty file rejected: {relpath}")
            continue
        try:
            content.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"undecodable file rejected: {relpath}")
    return errors


# --------------------------------------------------------------------------
# canonical manifest (Flow A step 3)
# --------------------------------------------------------------------------
def build_manifest(files: dict):
    """Sorted relative paths + content hash; manifest hash = corpus_version."""
    sorted_paths = sorted(files.keys())
    entries = []
    for p in sorted_paths:
        entries.append((p, sha256_hex(files[p])))
    manifest_hash = sha256_hex("\n".join(f"{p}\t{h}" for p, h in entries).encode("utf-8"))
    return manifest_hash, entries


# --------------------------------------------------------------------------
# deterministic heading-aware chunking (Flow A step 4)
# --------------------------------------------------------------------------
def chunk_document(relpath: str, content: str, chunk_size: int, overlap: int) -> list:
    """
    Chunking keeps heading lines at chunk boundaries, then enforces chunk_size
    with line-granularity overflow, then re-attaches `overlap` tail chars from
    the previous chunk. Deterministic: same input -> same chunks.
    """
    lines = content.splitlines()
    base = []
    current = []
    current_len = 0
    for line in lines:
        if line.lstrip().startswith("#") and current:
            base.append("\n".join(current))
            current, current_len = [], 0
        current.append(line)
        current_len += len(line) + 1
        while current_len > chunk_size and len(current) > 1:
            dropped = current.pop(0)
            current_len -= len(dropped) + 1
    if current:
        base.append("\n".join(current))

    if len(base) <= 1:
        return [c for c in base if c.strip()]

    out = [base[0]]
    for prev, nxt in zip(base, base[1:]):
        prefix = prev[-overlap:] if overlap > 0 else ""
        out.append((prefix + "\n" + nxt).strip() if prefix else nxt)
    return [c for c in out if c.strip()]


# --------------------------------------------------------------------------
# embedding adapter (HTTP OpenAI-compatible, bounded timeout)
# --------------------------------------------------------------------------
def http_embed_fn(base_url: str, model: str, timeout_ms: int):
    """Returns embed(texts) -> vectors; raises TimeoutFailure/ProviderFailure."""

    def fn(texts, timeout_ms=timeout_ms):
        body = json.dumps({"model": model, "input": texts}).encode("utf-8")
        req = urllib.request.Request(
            base_url.rstrip("/") + "/v1/embeddings",
            data=body,
            headers={"Content-Type": "application/json",
                     "Authorization": "Bearer test-key"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_ms / 1000.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (socket.timeout, TimeoutError) as exc:
            raise TimeoutFailure(f"embedding timeout after {timeout_ms}ms") from exc
        except urllib.error.HTTPError as exc:
            raise ProviderFailure(f"embedding http {exc.code}") from exc
        except urllib.error.URLError as exc:
            reason = getattr(exc, "reason", None)
            if isinstance(reason, (socket.timeout, TimeoutError)):
                raise TimeoutFailure(f"embedding timeout after {timeout_ms}ms") from exc
            raise ProviderFailure(f"embedding transport error: {exc}") from exc
        items = data.get("data", [])
        items.sort(key=lambda d: d.get("index", 0))
        vectors = [d.get("embedding") for d in items]
        if not vectors or any(v is None for v in vectors):
            raise ProviderFailure("embedding response missing data")
        return vectors

    return fn


# --------------------------------------------------------------------------
# pipeline (Flow A orchestration)
# --------------------------------------------------------------------------
def run_ingestion(store, files, config, embed_fn, correlation_id="ingest-test"):
    """
    Returns result dict:
      {status: "active"|"duplicate"|"failed", corpus_version, document_count,
       chunk_count, error_category?}
    On failure: candidate marked failed, active version + chunks untouched,
    sanitized safe event recorded (no payload/body).
    """
    started = time.time()
    manifest_hash = None
    try:
        errors = validate_corpus(files)
        if errors:
            raise ValidationFailure("corpus invalid: " + "; ".join(errors[:5]))

        manifest_hash, entries = build_manifest(files)

        # identical manifest rerun -> no-op (AC-003)
        if store.settings["active_corpus_version"] == manifest_hash:
            return {
                "status": "duplicate",
                "corpus_version": manifest_hash,
                "document_count": len(entries),
                "chunk_count": store.versions[manifest_hash]["chunk_count"] if manifest_hash in store.versions else 0,
            }

        config_revision = config.config_revision
        profile_id = config.profile_id()

        # embedding-profile guard: candidate profile must equal active profile
        # once a corpus exists (index/query identical profile, ADR-002)
        active_profile = store.settings["embedding_profile_id"]
        if active_profile is not None and active_profile != profile_id:
            raise ValidationFailure(
                "embedding profile mismatch: active corpus uses different embedding profile; full re-ingest required")

        store.prepare_staging(manifest_hash, profile_id, config_revision)

        chunks_per_doc = {}
        chunk_texts = []
        for relpath, source_hash in entries:
            content = files[relpath].decode("utf-8")
            chunks = chunk_document(relpath, content, config.chunk_size, config.chunk_overlap)
            chunks_per_doc[relpath] = (source_hash, chunks)
            chunk_texts.extend(chunks)

        # single embedding profile for every chunk (ADR-002)
        vectors = embed_fn(chunk_texts, timeout_ms=config.embed_timeout_ms)

        # dimension validation against config/embedding profile
        for vec in vectors:
            if len(vec) != config.embedding_dimension:
                raise ValidationFailure(
                    f"embedding dimension mismatch: expected {config.embedding_dimension}, got {len(vec)}")

        # staging writes
        idx = 0
        for relpath, (source_hash, chunks) in sorted(chunks_per_doc.items()):
            for chunk_index, chunk in enumerate(chunks):
                metadata = {
                    "source_name": relpath,
                    "source_hash": source_hash,
                    "chunk_index": chunk_index,
                    "corpus_version": manifest_hash,
                    "embedding_profile_id": profile_id,
                }
                store.write_staging_document(manifest_hash, source_hash, chunk_index,
                                             chunk, vectors[idx], metadata)
                idx += 1
            store.finish_staging_document(manifest_hash)

        # candidate validation: counts + metadata completeness
        expected_docs = len(entries)
        actual_docs = store.versions[manifest_hash]["document_count"]
        actual_chunks = store.versions[manifest_hash]["chunk_count"]
        if actual_docs != expected_docs or actual_chunks != len(chunk_texts):
            raise DatabaseFailure(
                f"candidate validation failed: docs {actual_docs}/{expected_docs}, "
                f"chunks {actual_chunks}/{len(chunk_texts)}")
        for key, rec in store.documents.items():
            meta = rec["metadata"]
            required = {"source_name", "source_hash", "chunk_index", "corpus_version", "embedding_profile_id"}
            missing = required - set(meta.keys())
            if missing:
                raise ValidationFailure(f"chunk metadata missing: {sorted(missing)}")

        # atomic activation (single-lock pointer swap)
        store.activate(manifest_hash, profile_id, config_revision)

        store.record_safe_event(correlation_id=correlation_id, workflow="ingestion",
                                stage="activation", status="success",
                                duration_ms=int((time.time() - started) * 1000),
                                error_category=None,
                                config_revision=config_revision,
                                corpus_version=manifest_hash)

        return {
            "status": "active",
            "corpus_version": manifest_hash,
            "document_count": actual_docs,
            "chunk_count": actual_chunks,
        }

    except (TimeoutFailure, ProviderFailure, ValidationFailure, DatabaseFailure) as exc:
        store.mark_failed(manifest_hash, str(exc), type(exc).__name__)
        return {
            "status": "failed",
            "corpus_version": manifest_hash,
            "document_count": 0,
            "chunk_count": 0,
            "error_category": type(exc).__name__,
        }