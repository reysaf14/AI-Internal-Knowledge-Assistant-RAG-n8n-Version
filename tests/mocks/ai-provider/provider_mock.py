# Provider Mock — OpenAI-Compatible HTTP Server for Chat + Embeddings
# Architecture version: 1.2 | For local-isolated testing only
# =============================================================================
# This mock implements the OpenAI-compatible contract required by ADR-002:
# - POST /v1/chat/completions  → chat completion
# - POST /v1/embeddings        → embeddings
# - GET  /health               → health check
# - GET  /v1/models            → model list
#
# Run: python provider_mock.py
# Default port: 8080 (configurable via PORT env var)
# =============================================================================

import os
import json
import time
import hashlib
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
PORT = int(os.getenv("PORT", "8080"))
MOCK_CHAT_MODEL = "mock-chat-model-v1"
MOCK_EMBEDDING_MODEL = "mock-embedding-model-v1"
MOCK_EMBEDDING_DIM = 384  # Fixed dimension for testing

# Deterministic responses for known test questions
DETERMINISTIC_RESPONSES = {
    "jam berapa toko buka hari senin": {
        "answer": "Toko buka pukul 08:00 pada hari Senin. [CITATION:0]",
        "citations": [{"key": "0", "source_name": "09_FAQ_Jam_Operasional_dan_Lokasi.md"}]
    },
    "bagaimana prosedur membuka toko menurut sop": {
        "answer": "Prosedur buka toko dimulai 07:30 oleh manajer: buka kunci & alarm, nyalakan lampu/AC/POS, cek uang kembalian minimal Rp 500.000, inspeksi kebersihan, cek harga etalase, briefing tim, buka pintu 08:00. [CITATION:0]",
        "citations": [{"key": "0", "source_name": "01_SOP_Buka_Toko.md"}]
    },
    "apa saja isi sop penanganan kas dan setoran harian": {
        "answer": "SOP mengatur: penerimaan uang kembalian awal hari, pencatatan transaksi, cek kas fisik vs POS tiap 2 jam (selisih > Rp 50.000 dilaporkan), hitung total kas akhir hari, bandingkan dengan POS, isi formulir setoran, serahkan ke manajer. Selisih > Rp 100.000 wajib investigasi. [CITATION:0]",
        "citations": [{"key": "0", "source_name": "03_SOP_Penanganan_Kas_dan_Setoran_Harian.md"}]
    },
    "berapa hari cuti tahunan karyawan setelah 1 tahun kerja": {
        "answer": "12 hari per tahun. [CITATION:0]",
        "citations": [{"key": "0", "source_name": "20_Kebijakan_Cuti_dan_Izin_Karyawan.md"}]
    },
    "bagaimana ketentuan izin sakit kurang dari 3 hari": {
        "answer": "Wajib surat keterangan dokter atau puskesmas. [CITATION:0]",
        "citations": [{"key": "0", "source_name": "20_Kebijakan_Cuti_dan_Izin_Karyawan.md"}]
    },
    "berapa bonus bulanan jika pencapaian penjualan 115%": {
        "answer": "Bonus Rp 1.000.000 (pencapaian 111-120%). [CITATION:0]",
        "citations": [{"key": "0", "source_name": "24_Kebijakan_Bonus_dan_Insentif_Penjualan.md"}]
    },
    "apakah toko menyediakan parkir untuk pelanggan": {
        "answer": "Ya, parkir motor 20 unit dan mobil 5 unit di depan toko, gratis 2 jam pertama. [CITATION:0]",
        "citations": [{"key": "0", "source_name": "09_FAQ_Jam_Operasional_dan_Lokasi.md"}]
    },
    "apa prosedur tutup toko pada pukul 21:00": {
        "answer": "Tutup pintu masuk 21:00, layani pelanggan sisa, tutup kasir 21:15 (hitung kas, catat, setor ke manajer), matikan POS/AC/lampu 21:25, cek kebersihan & kunci gudang/kantor 21:30, aktifkan alarm & kunci utama 21:35. [CITATION:0]",
        "citations": [{"key": "0", "source_name": "02_SOP_Tutup_Toko.md"}]
    },
    "bagaimana kebijakan k3 terkait apar dan jalur evakuasi": {
        "answer": "APAR di kasir (1), gudang (2), kantor (1). Jalur evakuasi: pintu depan & pintu belakang gudang. Simulasi 2x/tahun. [CITATION:0]",
        "citations": [{"key": "0", "source_name": "25_Kebijakan_Keselamatan_Kerja_K3_Sederhana.md"}]
    },
    "di mana lokasi toko makmur jaya": {
        "answer": "Jalan Merdeka No. 123, Jakarta Pusat, dekat Stasiun Merdeka. [CITATION:0]",
        "citations": [{"key": "0", "source_name": "00_Company_Profile_Toko_Makmur_Jaya.md"}]
    },
    "apa syarat mendapatkan bonus tahunan (thr + performance)": {
        "answer": "Karyawan status tetap, minimal 6 bulan kerja, tidak ada sanksi berat tahun berjalan. THR 1x gaji pokok, performance bonus 0.5-2x gaji pokok. [CITATION:0]",
        "citations": [{"key": "0", "source_name": "24_Kebijakan_Bonus_dan_Insentif_Penjualan.md"}]
    },
    "berapa lama cuti melahirkan yang diberikan": {
        "answer": "3 bulan (1,5 bulan sebelum dan 1,5 bulan setelah melahirkan) sesuai UU. [CITATION:0]",
        "citations": [{"key": "0", "source_name": "20_Kebijakan_Cuti_dan_Izin_Karyawan.md"}]
    },
    "apa yang harus dilakukan jika lantai basah di area kerja": {
        "answer": "Pasang tanda 'Hati-hati Lantai Licin' secara wajib. [CITATION:0]",
        "citations": [{"key": "0", "source_name": "25_Kebijakan_Keselamatan_Kerja_K3_Sederhana.md"}]
    },
}

UNSUPPORTED_RESPONSE = {
    "answer": "Informasi tidak ditemukan di dokumen resmi.",
    "citations": []
}

# -----------------------------------------------------------------------------
# Pydantic Models (OpenAI-compatible)
# -----------------------------------------------------------------------------
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.0
    max_tokens: Optional[int] = 500
    stream: Optional[bool] = False

class EmbeddingRequest(BaseModel):
    model: str
    input: List[str] | str
    encoding_format: Optional[str] = "float"

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "mock-provider"

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def deterministic_embedding(text: str) -> List[float]:
    """Generate deterministic embedding vector from text."""
    # Use SHA-256 hash to create deterministic pseudo-random vector
    hash_obj = hashlib.sha256(text.encode('utf-8'))
    hash_bytes = hash_obj.digest()
    
    # Convert to float vector of fixed dimension
    vector = []
    for i in range(MOCK_EMBEDDING_DIM):
        byte_idx = i % len(hash_bytes)
        # Normalize to [-1, 1] range
        val = (hash_bytes[byte_idx] / 255.0) * 2 - 1
        vector.append(val)
    
    # Normalize to unit length (cosine similarity ready)
    norm = sum(v*v for v in vector) ** 0.5
    if norm > 0:
        vector = [v / norm for v in vector]
    
    return vector

def find_deterministic_response(question: str, context: str = "") -> Dict[str, Any]:
    """Find deterministic response for known test questions."""
    question_lower = question.lower().strip()
    
    # Check for exact match in deterministic responses
    for key, response in DETERMINISTIC_RESPONSES.items():
        if key in question_lower:
            return response
    
    # Check if any context contains known keywords (unsupported)
    unsupported_keywords = ["gaji pokok", "nama pemilik", "pinjaman ke manajer", "presiden indonesia"]
    for kw in unsupported_keywords:
        if kw in question_lower:
            return UNSUPPORTED_RESPONSE
    
    # Default: return unsupported for unknown questions
    return UNSUPPORTED_RESPONSE

# -----------------------------------------------------------------------------
# FastAPI App
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Mock AI Provider (OpenAI-Compatible)",
    description="Deterministic mock for chat completions and embeddings. For local-isolated testing only.",
    version="1.0.0"
)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "mock-ai-provider",
        "version": "1.0.0",
        "chat_model": MOCK_CHAT_MODEL,
        "embedding_model": MOCK_EMBEDDING_MODEL,
        "embedding_dimension": MOCK_EMBEDDING_DIM
    }

@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)."""
    return {
        "object": "list",
        "data": [
            ModelInfo(id=MOCK_CHAT_MODEL).model_dump(),
            ModelInfo(id=MOCK_EMBEDDING_MODEL).model_dump()
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Chat completions endpoint (OpenAI-compatible)."""
    # Validate model
    if request.model not in [MOCK_CHAT_MODEL, MOCK_EMBEDDING_MODEL]:
        raise HTTPException(status_code=400, detail=f"Model '{request.model}' not found. Available: {MOCK_CHAT_MODEL}, {MOCK_EMBEDDING_MODEL}")
    
    # Extract user question (last user message)
    user_messages = [msg for msg in request.messages if msg.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found")
    
    question = user_messages[-1].content
    
    # Find deterministic response
    response_data = find_deterministic_response(question)
    
    # Build OpenAI-compatible response
    response = {
        "id": f"chatcmpl-mock-{int(time.time() * 1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": response_data["answer"]
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": len(question.split()),
            "completion_tokens": len(response_data["answer"].split()),
            "total_tokens": len(question.split()) + len(response_data["answer"].split())
        }
    }
    
    # Add citations as a custom field (workflow can parse this)
    if response_data["citations"]:
        response["citations"] = response_data["citations"]
    
    return JSONResponse(content=response)

@app.post("/v1/embeddings")
async def embeddings(request: EmbeddingRequest):
    """Embeddings endpoint (OpenAI-compatible)."""
    # Validate model
    if request.model != MOCK_EMBEDDING_MODEL:
        raise HTTPException(status_code=400, detail=f"Model '{request.model}' not found for embeddings. Use '{MOCK_EMBEDDING_MODEL}'")
    
    # Normalize input to list
    texts = request.input if isinstance(request.input, list) else [request.input]
    
    # Generate embeddings
    embedding_data = []
    for i, text in enumerate(texts):
        embedding_data.append({
            "object": "embedding",
            "index": i,
            "embedding": deterministic_embedding(text)
        })
    
    return {
        "object": "list",
        "data": embedding_data,
        "model": request.model,
        "usage": {
            "prompt_tokens": sum(len(t.split()) for t in texts),
            "total_tokens": sum(len(t.split()) for t in texts)
        }
    }

# -----------------------------------------------------------------------------
# Error Handlers
# -----------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Internal server error",
                "type": "internal_error",
                "code": "internal_error"
            }
        }
    )

# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Starting Mock AI Provider on port {PORT}")
    print(f"Chat model: {MOCK_CHAT_MODEL}")
    print(f"Embedding model: {MOCK_EMBEDDING_MODEL} (dim={MOCK_EMBEDDING_DIM})")
    print(f"Health: http://localhost:{PORT}/health")
    print(f"Models: http://localhost:{PORT}/v1/models")
    print(f"Chat:   http://localhost:{PORT}/v1/chat/completions")
    print(f"Emb:    http://localhost:{PORT}/v1/embeddings")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")