#!/usr/bin/env python3
# =============================================================================
# telegram_delivery_core.py — contract-level Telegram delivery orchestrator
# (MIRROR of workflow 02 — Telegram transport layer)
# =============================================================================
# Mirrors: workflow 02, Flow B step 1-3 + delivery state + deadline
# Scope: webhook validation, chat authorization, atomic dedup, bounded
#        AI calls, delivery state, timing instrumentation.
#
# NOT production n8n code. In-process Python for self-test only.
# Import verification (AC-025) is deferred to M6 (DevOps).
#
# Architecture version: 1.2 | Acceptance Matrix: 1.0
# Config revision: 2026-09-14-m2-provisional
# Date: 2026-09-14
# Status: M4 harness — for self-test use only
# =============================================================================

import hashlib
import json
import os
import time
import threading
import urllib.error
import urllib.request

# shared harness
import rag_qa_core as qa_core


# ===========================================================================
# Constants
# ===========================================================================

BUSINESS_DEADLINE_MS = 5000   # <5s from receive to Telegram send success
MIN_SAFE_BUDGET_MS = 300      # minimum remaining budget to attempt send


# ===========================================================================
# Delivery states
# ===========================================================================

class DeliveryState:
    DELIVERED = "delivered"
    FAILED = "failed"
    DELIVERY_UNKNOWN = "delivery_unknown"


# ===========================================================================
# TelegramUpdate — sanitized representation
# ===========================================================================

class TelegramUpdate:
    """Minimal sanitized Telegram update for harness testing.

    Stores only what's needed: update_id, chat_id, text.
    No raw payload, no user PII beyond what's required for validation.
    """

    def __init__(self, update_id, chat_id, text, message=None):
        self.update_id = update_id
        self.chat_id = chat_id
        self.text = text  # stripped text; None if no message or no text
        self.raw = message  # optional: full message dict for structure checks

    @classmethod
    def from_telegram_payload(cls, payload):
        """Parse a synthetic Telegram update payload (JSONL fixture format).

        Returns a TelegramUpdate or None if the payload has no processable
        message/text structure (e.g., callback_query).
        """
        update_id = payload.get("update_id")
        msg = payload.get("message")
        if not msg or not isinstance(msg, dict):
            # not a message update — stop before retrieval/model (AC-007)
            return cls(update_id=update_id, chat_id=None, text=None, message=None)

        chat = msg.get("chat", {})
        chat_id = chat.get("id")
        text = msg.get("text")
        if text is not None:
            text = str(text).strip()  # "" if empty/whitespace-only

        return cls(
            update_id=update_id,
            chat_id=chat_id,
            text=text,
            message=msg,
        )


# ===========================================================================
# DedupStore — atomic claim for update dedup
# ===========================================================================

class DedupStore:
    """Thread-safe atomic claim store for Telegram update deduplication.

    Identity = bot runtime scope + update_id (architecture §5).
    In harness: identity = prefix + update_id (no real bot token used).

    States: "claimed" → "delivered" | "failed" | "delivery_unknown"
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._claims = {}  # key → state string

    def try_claim(self, key):
        """Atomically claim an update_id. Returns True if this caller wins.

        If already claimed, returns False (no-op for this execution).
        """
        with self._lock:
            if key in self._claims:
                return False
            self._claims[key] = "claimed"
            return True

    def set_state(self, key, state):
        """Update the state of a claimed update (delivered/failed/unknown)."""
        with self._lock:
            if key in self._claims:
                self._claims[key] = state

    def get_state(self, key):
        """Get current state of an update claim."""
        with self._lock:
            return self._claims.get(key)

    def is_claimed(self, key):
        """Check if an update has been claimed (regardless of final state)."""
        with self._lock:
            return key in self._claims


# ===========================================================================
# Mock Telegram Send
# ===========================================================================

class MockTelegramSend:
    """Deterministic mock for Telegram sendMessage API.

    Supports fault injection: delay, error status, ambiguous result.
    Records all send attempts for assertion.
    """

    def __init__(self):
        self.attempts = []          # list of dicts: chat_id, text_length, timeout_ms
        self.send_delay_ms = 0      # artificial delay
        self.send_error = None      # exception to raise
        self.send_ambiguous = False  # connection reset after request
        self.send_status = 200      # HTTP status to return
        self._lock = threading.Lock()

    def __call__(self, chat_id, text, timeout_ms=2000):
        with self._lock:
            self.attempts.append({
                "chat_id": chat_id,
                "text": text,
                "text_length": len(text),
                "timeout_ms": timeout_ms,
            })

        if self.send_delay_ms > 0:
            time.sleep(self.send_delay_ms / 1000.0)

        if self.send_error:
            raise self.send_error

        if self.send_ambiguous:
            return {"status": "ambiguous", "sent": True, "acknowledged": False}

        if self.send_status != 200:
            return {"status": "error", "sent": False, "acknowledged": False,
                    "http_status": self.send_status}

        return {"status": "sent", "sent": True, "acknowledged": True}

    @property
    def attempt_count(self):
        with self._lock:
            return len(self.attempts)

    def reset(self):
        with self._lock:
            self.attempts = []
            self.send_delay_ms = 0
            self.send_error = None
            self.send_ambiguous = False
            self.send_status = 200


# ===========================================================================
# Delivery pipeline
# ===========================================================================

def run_delivery_pipeline(
    update,           # TelegramUpdate
    dedup_store,      # DedupStore
    rag_store,        # ingest_core.Store (from M2)
    embed_fn,         # embedding function
    chat_fn,          # chat function
    send_fn,          # MockTelegramSend or real send function
    settings,         # qa_core.QASettings
    allowed_chat_id,  # expected chat_id (str or int)
    deadline_ms=BUSINESS_DEADLINE_MS,
):
    """Run the full Telegram Q&A delivery pipeline with deadline enforcement.

    Flow (architecture Flow B):
      1. Validate update structure (AC-007)
      2. Check chat authorization (AC-007)
      3. Atomic dedup claim (AC-008)
      4. Run QA core: embed → retrieve → chat → citation validate (AC-011..020)
      5. Send to Telegram (AC-009, AC-010)
      6. Record delivery state (AC-009, AC-023)

    Returns a dict with: status, duration_ms, error_category, send_attempts,
    safe_events.
    """
    started = time.time()
    send_attempts = 0
    safe_events = []

    def elapsed_ms():
        return int((time.time() - started) * 1000)

    def remaining_ms():
        return max(0, deadline_ms - elapsed_ms())

    # ------------------------------------------------------------------
    # Step 1: Validate update structure (AC-007)
    # ------------------------------------------------------------------
    # text is None → no message or no text field (non_message)
    # text is ""   → message exists but text is empty (empty_text)
    if update.text is None:
        return {
            "status": "stopped",
            "reason": "non_message",
            "duration_ms": elapsed_ms(),
            "error_category": None,
            "send_attempts": 0,
            "safe_events": safe_events,
        }

    if not update.text:  # empty string
        return {
            "status": "stopped",
            "reason": "empty_text",
            "duration_ms": elapsed_ms(),
            "error_category": None,
            "send_attempts": 0,
            "safe_events": safe_events,
        }

    # ------------------------------------------------------------------
    # Step 2: Check chat authorization (AC-007)
    # ------------------------------------------------------------------
    if str(update.chat_id) != str(allowed_chat_id):
        return {
            "status": "stopped",
            "reason": "unauthorized_chat",
            "duration_ms": elapsed_ms(),
            "error_category": None,
            "send_attempts": 0,
            "safe_events": safe_events,
        }

    # ------------------------------------------------------------------
    # Step 3: Atomic dedup claim (AC-008)
    # ------------------------------------------------------------------
    dedup_key = f"bot:webhook:{update.update_id}"
    if not dedup_store.try_claim(dedup_key):
        return {
            "status": "no_op",
            "reason": "duplicate_update",
            "duration_ms": elapsed_ms(),
            "error_category": None,
            "send_attempts": 0,
            "safe_events": safe_events,
        }

    # ------------------------------------------------------------------
    # Step 4: Run QA core (with failure → service-unavailable)
    # ------------------------------------------------------------------
    response_text = None
    try:
        # budget check before AI
        if remaining_ms() <= MIN_SAFE_BUDGET_MS:
            raise _BudgetExceeded("budget exhausted before AI step")

        qa_result = qa_core.run_qa(
            rag_store, update.text, embed_fn, chat_fn, settings
        )

        if qa_result["status"] == "unavailable":
            response_text = qa_core.UNAVAILABLE
        elif qa_result["status"] == "abstained":
            response_text = qa_result["answer"]
        else:
            # answered: include sources for Telegram display
            response_text = qa_result["answer"]
            if qa_result.get("sources"):
                response_text += "\n\nSumber: " + ", ".join(qa_result["sources"])

    except Exception as exc:
        # failure branch: deterministic service-unavailable
        response_text = qa_core.UNAVAILABLE
        safe_events.append({
            "stage": "qa",
            "error_category": _classify_error(exc),
            "duration_ms": elapsed_ms(),
        })

    # ------------------------------------------------------------------
    # Step 5: Send to Telegram (bounded by remaining budget)
    # ------------------------------------------------------------------
    send_budget = remaining_ms()

    if send_budget <= 0:
        # timeout before send even attempted → delivery_unknown
        dedup_store.set_state(dedup_key, DeliveryState.DELIVERY_UNKNOWN)
        return {
            "status": DeliveryState.DELIVERY_UNKNOWN,
            "duration_ms": elapsed_ms(),
            "error_category": "deadline_exceeded_before_send",
            "send_attempts": 0,
            "safe_events": safe_events,
        }

    try:
        send_result = send_fn(update.chat_id, response_text,
                              timeout_ms=min(send_budget, 3000))
        send_attempts += 1

        if send_result.get("status") == "sent":
            dedup_store.set_state(dedup_key, DeliveryState.DELIVERED)
            return {
                "status": DeliveryState.DELIVERED,
                "duration_ms": elapsed_ms(),
                "error_category": None,
                "send_attempts": send_attempts,
                "safe_events": safe_events,
            }
        elif send_result.get("status") == "ambiguous":
            # connection reset after request — outcome unknown
            dedup_store.set_state(dedup_key, DeliveryState.DELIVERY_UNKNOWN)
            return {
                "status": DeliveryState.DELIVERY_UNKNOWN,
                "duration_ms": elapsed_ms(),
                "error_category": "delivery_ambiguous",
                "send_attempts": send_attempts,
                "safe_events": safe_events,
            }
        else:
            # explicit error from Telegram API
            dedup_store.set_state(dedup_key, DeliveryState.FAILED)
            return {
                "status": DeliveryState.FAILED,
                "duration_ms": elapsed_ms(),
                "error_category": "send_error",
                "send_attempts": send_attempts,
                "safe_events": safe_events,
            }

    except Exception as exc:
        # send exception
        dedup_store.set_state(dedup_key, DeliveryState.FAILED)
        return {
            "status": DeliveryState.FAILED,
            "duration_ms": elapsed_ms(),
            "error_category": "send_exception",
            "send_attempts": send_attempts,
            "safe_events": safe_events,
        }


# ===========================================================================
# Error classification (safe, no payload)
# ===========================================================================

class _BudgetExceeded(Exception):
    pass


def _classify_error(exc):
    """Classify exception to safe category string (no payload/stack)."""
    name = type(exc).__name__
    if "Timeout" in name or "TimeoutError" in name:
        return "timeout"
    if "Provider" in name:
        return "provider_failure"
    if "Config" in name:
        return "config_failure"
    if "Budget" in name:
        return "deadline_exceeded"
    return "unknown_error"
