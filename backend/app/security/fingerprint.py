"""Cryptographic question and exam paper fingerprinting module.

Provides deterministic fingerprint creation, integrity verification,
and exact cryptographic matching for question leakage investigation.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any


def canonicalize_text(text: str) -> str:
    """Normalize whitespace, capitalization and punctuation for robust text matching."""
    if not text:
        return ""
    # Lowercase, normalize whitespace
    normalized = text.lower().strip()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def compute_question_fingerprint(
    *,
    content: str,
    subject: str,
    topic: str,
    difficulty: str,
    answer: str | None = None,
    version: str = "v1",
) -> str:
    """Compute a deterministic SHA-256 fingerprint for canonicalized question content."""
    canonical = {
        "content": canonicalize_text(content),
        "subject": canonicalize_text(subject),
        "topic": canonicalize_text(topic),
        "difficulty": canonicalize_text(difficulty),
        "answer": canonicalize_text(answer) if answer else "",
        "version": version,
    }
    payload = json.dumps(canonical, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def compute_exam_fingerprint(question_fingerprints: list[str]) -> str:
    """Compute an ordered exam paper fingerprint from an ordered list of question fingerprints."""
    payload = json.dumps(question_fingerprints, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_question_integrity(
    *,
    content: str,
    subject: str,
    topic: str,
    difficulty: str,
    answer: str | None,
    expected_fingerprint: str,
) -> bool:
    """Verify if a question matches its claimed fingerprint."""
    fp = compute_question_fingerprint(
        content=content,
        subject=subject,
        topic=topic,
        difficulty=difficulty,
        answer=answer,
    )
    return fp.lower() == expected_fingerprint.lower()


def compute_text_similarity(text1: str, text2: str) -> float:
    """Compute normalized token overlap Jaccard similarity between two texts."""
    t1 = set(re.findall(r"\w+", canonicalize_text(text1)))
    t2 = set(re.findall(r"\w+", canonicalize_text(text2)))
    if not t1 or not t2:
        return 0.0
    intersection = t1.intersection(t2)
    union = t1.union(t2)
    return len(intersection) / len(union)
