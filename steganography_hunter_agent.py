# Copyright 2025 Amazon.com and its affiliates; all rights reserved.
# This file is Amazon Web Services Content and may not be distributed without permission.

"""
Steganography Hunter Agent - Hidden Message Detection
Deterministic detection for acrostic messages and numeric encoding schemes.
"""

import re
from typing import Iterable, List, Optional

from strands import tool


def _format_result(message: str) -> str:
    cleaned = re.sub(r"\s+", " ", message.strip())
    return cleaned.upper()


def _first_letters_of_lines(text: str) -> str:
    letters = [line.strip()[0] for line in text.splitlines() if line.strip()]
    return "".join(letters)


def _first_letters_of_words(text: str) -> str:
    letters: List[str] = []
    for line in text.splitlines():
        words = [word for word in re.findall(r"[A-Za-z0-9]+", line)]
        if words:
            letters.append(words[0][0])
    return "".join(letters)


def _first_letters_of_sentences(text: str) -> str:
    sentences = re.split(r"[.!?]+", text)
    letters = [sentence.strip()[0] for sentence in sentences if sentence.strip()]
    return "".join(letters)


def _pick_acrostic_candidate(candidates: Iterable[str]) -> Optional[str]:
    for candidate in candidates:
        cleaned = re.sub(r"[^A-Za-z]", "", candidate)
        if cleaned:
            return cleaned
    return None


@tool
def acrostic_detector(text: str) -> str:
    """Detect acrostic messages deterministically."""
    try:
        candidates = [
            _first_letters_of_lines(text),
            _first_letters_of_words(text),
            _first_letters_of_sentences(text),
        ]
        message = _pick_acrostic_candidate(candidates)
        if message:
            return f"DECODED: {_format_result(message)}"
        return "NO HIDDEN MESSAGE DETECTED"
    except Exception as exc:
        return f"Error detecting acrostic messages: {exc}"


def _tokenize_numbers(text: str) -> List[str]:
    return re.findall(r"-?\d+", text)


def _try_a1z26(tokens: List[str]) -> Optional[str]:
    decoded_chars: List[str] = []
    for token in tokens:
        value = int(token)
        if value == 0:
            decoded_chars.append(" ")
            continue
        if 1 <= value <= 26:
            decoded_chars.append(chr(ord("A") + value - 1))
        else:
            return None
    if decoded_chars:
        return "".join(decoded_chars)
    return None


@tool
def numeric_encoding_decoder(text: str) -> str:
    """Decode numeric encodings (focus on A1Z26)."""
    try:
        tokens = _tokenize_numbers(text)
        if not tokens:
            return "NO VALID ENCODING DETECTED"
        a1z26 = _try_a1z26(tokens)
        if a1z26:
            return f"DECODED: {_format_result(a1z26)}"
        return "NO VALID ENCODING DETECTED"
    except Exception as exc:
        return f"Error decoding numeric encoding: {exc}"
