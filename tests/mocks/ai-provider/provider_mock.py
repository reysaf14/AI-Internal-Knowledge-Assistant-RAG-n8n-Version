#!/usr/bin/env python3
# =============================================================================
# Provider Mock — OpenAI-Compatible HTTP Server (stdlib-only)
# Asisten Pengetahuan Internal Toko Makmur Jaya
# Architecture version: 1.2 | ADR-002 provider-neutral boundary
# =============================================================================
# This mock implements the OpenAI-compatible contract required by ADR-002:
#   GET  /health                -> health check (chat/embedding model identity)
#   GET  /v1/models             -> model list
#   POST /v1/chat/completions   -> chat completion (deterministic)
#   POST /v1/embeddings         -> embeddings (deterministic)
#
# Stdlib-only (http.server) so tests run with zero extra dependencies and so
# the n8n HTTP Request node can call it the same way as any OpenAI-compatible
# endpoint (hosted or private/self-hosted).
#
# FAULT-INJECTION (read live at request time, set via environment):
#   MOCK_CHAT_MODEL        chat model id        (default mock-chat-model-v1)
#   MOCK_EMBEDDING_MODEL   embedding model id   (default mock-embedding-model-v1)
#   MOCK_EMBEDDING_DIM     embedding dimension  (default 384)
#   MOCK_EMBED_DELAY_MS    embedding delay      (default 0) -> ingest timeout tests
#   MOCK_EMBED_STATUS      embedding status     (default 0 = ok) -> auth/5xx tests
#   MOCK_CHAT_DELAY_MS     chat delay           (default 0) -> Q&A timeout tests
#   MOCK_CHAT_STATUS       chat status          (default 0 = ok) -> Q&A provider fail
#   MOCK_CHAT_GARBLED      return bad JSON      (default false) -> malformed output tests
#   MOCK_EXPECTED_TOKEN    require Bearer <token> if set -> auth tests
#   MOCK_LOG               true to log requests (default false)
#
# Usage:
#   python provider_mock.py            # serve on PORT (default 8080)
#   PORT=9090 python provider_mock.py  # serve on 9090
# =============================================================================

import hashlib
import json
import os
import re
import socket
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

PORT = int(os.getenv("PORT", "8080"))

# ---------------- deterministic chat responses (local-isolated fixtures) ----
DETERMINISTIC_RESPONSES = {
    "jam berapa toko buka hari senin": (
        "Toko buka pukul 08:00 pada hari Senin. [CITATION:0]",
        ["09_FAQ_Jam_Operasional_dan_Lokasi.md"],
    ),
    "bagaimana prosedur membuka toko menurut sop": (
        "Prosedur buka toko dimulai 07:30 oleh manajer: buka kunci & alarm, "
        "nyalakan lampu/AC/POS, cek uang kembalian minimal Rp 500.000, "
        "inspeksi kebersihan, cek harga etalase, briefing tim, buka pintu 08:00. [CITATION:0]",
        ["01_SOP_Buka_Toko.md"],
    ),
    "apa saja isi sop penanganan kas dan setoran harian": (
        "SOP mengatur: penerimaan uang kembalian awal hari, pencatatan transaksi, "
        "cek kas fisik vs POS tiap 2 jam (selisih > Rp 50.000 dilaporkan), hitung "
        "total kas akhir hari, bandingkan dengan POS, isi formulir setoran, serahkan "
        "ke manajer. Selisih > Rp 100.000 wajib investigasi. [CITATION:0]",
        ["03_SOP_Penanganan_Kas_dan_Setoran_Harian.md"],
    ),
    "berapa hari cuti tahunan karyawan setelah 1 tahun kerja": (
        "12 hari per tahun. [CITATION:0]",
        ["20_Kebijakan_Cuti_dan_Izin_Karyawan.md"],
    ),
    "bagaimana ketentuan izin sakit kurang dari 3 hari": (
        "Wajib surat keterangan dokter atau puskesmas. [CITATION:0]",
        ["20_Kebijakan_Cuti_dan_Izin_Karyawan.md"],
    ),
    "apa kebijakan retur dan tukar barang": (
        "Barang dapat dikembalikan/ditukar sesuai kebijakan retur yang berlaku di toko. [CITATION:0]",
        ["11_FAQ_Kebijakan_Retur_dan_Tukar_Barang.md"],
    ),
    "bagaimana cara mengajukan komplain barang rusak": (
        "Ajukan komplain melalui prosedur yang ditetapkan, lampirkan bukti transaksi "
        "dan kondisi barang. [CITATION:0]",
        ["16_Panduan_Komplain_Barang_Rusak.md"],
    ),
    "apa yang harus dilakukan jika pengantaran terlambat": (
        "Ikuti panduan komplain keterlambatan pengantaran sesuai prosedur yang berlaku. [CITATION:0]",
        ["18_Panduan_Komplain_Keterlambatan_Pengantaran.md"],
    ),
    "apakah toko menyediakan parkir untuk pelanggan": (
        "Ya, parkir motor 20 unit dan mobil 5 unit di depan toko, gratis 2 jam pertama. [CITATION:0]",
        ["09_FAQ_Jam_Operasional_dan_Lokasi.md"],
    ),
    "apa prosedur tutup toko pada pukul 21:00": (
        "Tutup pintu masuk 21:00, layani pelanggan sisa, tutup kasir 21:15 (hitung "
        "kas, catat, setor ke manajer), matikan POS/AC/lampu 21:25, cek kebersihan "
        "& kunci gudang/kantor 21:30, aktifkan alarm & kunci utama 21:35. [CITATION:0]",
        ["02_SOP_Tutup_Toko.md"],
    ),
    "bagaimana kebijakan k3 terkait apar dan jalur evakuasi": (
        "APAR di kasir (1), gudang (2), kantor (1). Jalur evakuasi: pintu depan & "
        "pintu belakang gudang. Simulasi 2x/tahun. [CITATION:0]",
        ["25_Kebijakan_Keselamatan_Kerja_K3_Sederhana.md"],
    ),
    "di mana lokasi toko makmur jaya": (
        "Jalan Merdeka No. 123, Jakarta Pusat, dekat Stasiun Merdeka. [CITATION:0]",
        ["00_Company_Profile_Toko_Makmur_Jaya.md"],
    ),
}

UNSUPPORTED_ANSWER = "Informasi tidak ditemukan di dokumen resmi."


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _env(name, default):
    """Read env live at request time so tests can toggle fault modes."""
    return os.getenv(name, default)


def _now_ms():
    return int(time.time() * 1000)


def deterministic_embedding(text: str, dim: int):
    """Deterministic semantic-ish embedding: hashed bag-of-words + L2 norm.

    Texts sharing tokens get high cosine similarity (mimics real embedding
    models); unrelated texts get ~0. Deterministic for the same input.
    """
    STOPWORDS = {
        "yang", "dan", "di", "ke", "dari", "apa", "bagaimana", "apakah",
        "untuk", "dengan", "atau", "ini", "itu", "adalah", "tidak", "akan",
        "bisa", "dapat", "pada", "per", "juga", "sudah", "belum", "secara",
        "tersebut", "sebuah", "saya", "anda", "kami", "mereka", "atau",
        "dalam", "oleh", "agar", "jika", "karena", "maka", "serta",
    }
    tokens = [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS]
    vector = [0.0] * dim
    for t in set(tokens):
        slot = int(hashlib.sha256(t.encode("utf-8")).hexdigest()[:8], 16) % dim
        vector[slot] = 1.0  # binary bag-of-words
    norm = sum(v * v for v in vector) ** 0.5
    if norm > 0:
        vector = [v / norm for v in vector]
    return vector


def _find_chat_response(question: str):
    q = question.lower().strip()
    for key, (answer, sources) in DETERMINISTIC_RESPONSES.items():
        if key in q:
            return answer, sources
    for kw in ("gaji pokok", "nama pemilik", "pinjaman ke manajer", "presiden indonesia"):
        if kw in q:
            return UNSUPPORTED_ANSWER, []
    return UNSUPPORTED_ANSWER, []


def _error_body(message, err_type, code):
    return {
        "error": {
            "message": message,
            "type": err_type,
            "code": code,
        }
    }


class MockHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    # -- silence default logging unless MOCK_LOG=true ----------------------
    def log_message(self, fmt, *args):
        if _env("MOCK_LOG", "false").lower() == "true":
            super().log_message(fmt, *args)

    # -- helpers ------------------------------------------------------------
    def _send(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            # The timeout/abort fixture intentionally closes the client socket.
            # This is a test outcome, not a provider mock failure.
            return

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _auth_ok(self):
        expected = _env("MOCK_EXPECTED_TOKEN", "")
        if not expected:
            return True
        return self.headers.get("Authorization") == f"Bearer {expected}"

    def _reject_auth(self):
        self._send(
            401,
            _error_body("Invalid authentication credentials", "authentication_error", "invalid_api_key"),
        )

    def _route(self, path, body=None):
        if path == "/health":
            dim = int(_env("MOCK_EMBEDDING_DIM", "384"))
            return self._send(200, {
                "status": "healthy",
                "service": "mock-ai-provider",
                "chat_model": _env("MOCK_CHAT_MODEL", "mock-chat-model-v1"),
                "embedding_model": _env("MOCK_EMBEDDING_MODEL", "mock-embedding-model-v1"),
                "embedding_dimension": dim,
            })
        if path == "/v1/models":
            return self._send(200, {
                "object": "list",
                "data": [
                    {"id": _env("MOCK_CHAT_MODEL", "mock-chat-model-v1"),
                     "object": "model", "created": int(time.time()), "owned_by": "mock-provider"},
                    {"id": _env("MOCK_EMBEDDING_MODEL", "mock-embedding-model-v1"),
                     "object": "model", "created": int(time.time()), "owned_by": "mock-provider"},
                ],
            })
        if path == "/v1/chat/completions":
            model = _env("MOCK_CHAT_MODEL", "mock-chat-model-v1")
            # fault injection: chat status override first (auth/5xx tests)
            chat_status = int(_env("MOCK_CHAT_STATUS", "0"))
            if chat_status:
                return self._send(
                    chat_status,
                    _error_body("Injected chat failure", "injected_error", str(chat_status)),
                )
            # fault injection: artificial delay (timeout tests)
            chat_delay = int(_env("MOCK_CHAT_DELAY_MS", "0"))
            if chat_delay > 0:
                time.sleep(chat_delay / 1000.0)
            messages = (body or {}).get("messages", [])
            question = ""
            for msg in messages:
                if msg.get("role") == "user":
                    question = msg.get("content", "")
            # fault injection: garbled/malformed output
            if _env("MOCK_CHAT_GARBLED", "false").lower() == "true":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                raw = b"{invalid json\" choices\""
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                try:
                    self.wfile.write(raw)
                except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
                    pass
                return
            answer, sources = _find_chat_response(question)
            payload = {
                "id": f"chatcmpl-mock-{_now_ms()}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": answer},
                    "finish_reason": "stop",
                }],
                "usage": {
                    "prompt_tokens": len(question.split()),
                    "completion_tokens": len(answer.split()),
                    "total_tokens": len(question.split()) + len(answer.split()),
                },
            }
            if sources:
                payload["citations"] = [
                    {"key": str(i), "source_name": name} for i, name in enumerate(sources)
                ]
            return self._send(200, payload)
        if path == "/v1/embeddings":
            # fault injection: status override first (auth/5xx tests)
            fail_status = int(_env("MOCK_EMBED_STATUS", "0"))
            if fail_status:
                return self._send(
                    fail_status,
                    _error_body("Injected failure", "injected_error", str(fail_status)),
                )
            # fault injection: artificial delay (timeout tests)
            delay_ms = int(_env("MOCK_EMBED_DELAY_MS", "0"))
            if delay_ms > 0:
                time.sleep(delay_ms / 1000.0)

            model = _env("MOCK_EMBEDDING_MODEL", "mock-embedding-model-v1")
            dim = int(_env("MOCK_EMBEDDING_DIM", "384"))
            if (body or {}).get("model") != model:
                return self._send(
                    400,
                    _error_body(f"Model not found for embeddings: {body.get('model')}",
                                "invalid_request_error", "model_not_found"),
                )
            raw = (body or {}).get("input", [])
            texts = raw if isinstance(raw, list) else [raw]
            data = [
                {"object": "embedding", "index": i, "embedding": deterministic_embedding(t, dim)}
                for i, t in enumerate(texts)
            ]
            return self._send(200, {
                "object": "list",
                "data": data,
                "model": model,
                "usage": {
                    "prompt_tokens": sum(len(t.split()) for t in texts),
                    "total_tokens": sum(len(t.split()) for t in texts),
                },
            })
        return self._send(404, _error_body("Not found", "invalid_request_error", "not_found"))

    # -- HTTP verbs ----------------------------------------------------------
    def do_GET(self):
        path = urlparse(self.path).path
        if not self._auth_ok():
            return self._reject_auth()
        self._route(path)

    def do_POST(self):
        path = urlparse(self.path).path
        if not self._auth_ok():
            return self._reject_auth()
        try:
            body = self._read_json()
        except Exception:
            return self._send(400, _error_body("Invalid JSON body", "invalid_request_error", "bad_json"))
        self._route(path, body)


def serve(port: int = PORT, host: str = "127.0.0.1"):
    """Start blocking server. Tests run this in a background thread."""
    server = ThreadingHTTPServer((host, port), MockHandler)
    print(f"[mock-ai-provider] listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    print("[mock-ai-provider] OpenAI-compatible mock (stdlib)")
    print(f"  chat model      : {_env('MOCK_CHAT_MODEL', 'mock-chat-model-v1')}")
    print(f"  embedding model : {_env('MOCK_EMBEDDING_MODEL', 'mock-embedding-model-v1')}")
    print(f"  embedding dim   : {_env('MOCK_EMBEDDING_DIM', '384')}")
    print(f"  fault status    : {_env('MOCK_EMBED_STATUS', '0')} (0=ok)")
    print(f"  fault delay ms  : {_env('MOCK_EMBED_DELAY_MS', '0')}")
    print(f"  chat status     : {_env('MOCK_CHAT_STATUS', '0')} (0=ok)")
    print(f"  chat delay ms   : {_env('MOCK_CHAT_DELAY_MS', '0')}")
    print(f"  chat garbled    : {_env('MOCK_CHAT_GARBLED', 'false')}")
    serve(PORT, host="0.0.0.0")
