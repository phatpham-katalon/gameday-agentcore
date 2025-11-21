# Copyright 2025 Amazon.com and its affiliates; all rights reserved.
# This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

"""
Pattern Detective Agent - Pattern-Based Ciphers
Deterministic implementations for Morse code, Rail Fence, and Polybius square ciphers.
"""

import re
from typing import Dict, List

from strands import tool

# Morse code reference table
MORSE_TO_CHAR: Dict[str, str] = {
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    "--.": "G",
    "....": "H",
    "..": "I",
    ".---": "J",
    "-.-": "K",
    ".-..": "L",
    "--": "M",
    "-.": "N",
    "---": "O",
    ".--.": "P",
    "--.-": "Q",
    ".-.": "R",
    "...": "S",
    "-": "T",
    "..-": "U",
    "...-": "V",
    ".--": "W",
    "-..-": "X",
    "-.--": "Y",
    "--..": "Z",
    "-----": "0",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
}

# Key words we expect in decrypted pattern messages (used for scoring/spacing)
COMMON_PATTERN_WORDS: List[str] = [
    "LLAMA",
    "LLAMAS",
    "UNICORN",
    "UNICORNS",
    "HIDING",
    "HIDE",
    "HIDDEN",
    "IN",
    "MOUNTAIN",
    "BASE",
    "TWENTY",
    "THREE",
    "CODE",
    "PATTERN",
    "SECRET",
    "MESSAGE",
    "ATTACK",
    "COORDINATES",
    "EVIL",
    "LLAMA",
    "SYNdICATE".upper(),
    "NORTH",
    "SOUTH",
    "EAST",
    "WEST",
    "HILLS",
    "SUMMIT",
    "RENDEZVOUS",
]

# Polybius square mapping
POLYBIUS_SQUARE: Dict[str, str] = {
    "11": "A",
    "12": "B",
    "13": "C",
    "14": "D",
    "15": "E",
    "21": "F",
    "22": "G",
    "23": "H",
    "24": "I",
    "24/I": "J",  # optional convenience
    "25": "K",
    "31": "L",
    "32": "M",
    "33": "N",
    "34": "O",
    "35": "P",
    "41": "Q",
    "42": "R",
    "43": "S",
    "44": "T",
    "45": "U",
    "51": "V",
    "52": "W",
    "53": "X",
    "54": "Y",
    "55": "Z",
}


def _normalize_morse_input(encrypted_text: str) -> List[str]:
    """Tokenize Morse input and preserve word boundaries via '/' or '|' characters."""
    normalized = encrypted_text.strip().replace("|", "/")
    normalized = normalized.replace("   ", " / ")
    normalized = normalized.replace("/", " / ")
    tokens = [token for token in normalized.split() if token]
    return tokens


def _decode_morse(encrypted_text: str) -> str:
    tokens = _normalize_morse_input(encrypted_text)
    decoded_chars: List[str] = []
    for token in tokens:
        if token in {"/"}:
            decoded_chars.append(" ")
            continue
        letter = MORSE_TO_CHAR.get(token)
        if letter is None:
            raise ValueError(f"Unknown Morse symbol: {token}")
        decoded_chars.append(letter)
    decoded_message = "".join(decoded_chars)
    return re.sub(r"\s+", " ", decoded_message).strip()


def _rail_pattern(num_chars: int, rails: int) -> List[int]:
    """Return rail index for each character position."""
    pattern = []
    rail = 0
    direction = 1
    for _ in range(num_chars):
        pattern.append(rail)
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction
    return pattern


def _rail_fence_decode(cipher_text: str, rails: int) -> str:
    cleaned = "".join(ch for ch in cipher_text if not ch.isspace())
    length = len(cleaned)
    if rails <= 1 or rails >= length:
        return cleaned
    pattern = _rail_pattern(length, rails)
    counts = [pattern.count(r) for r in range(rails)]
    rail_chunks = {}
    index = 0
    for rail_index, count in enumerate(counts):
        rail_chunks[rail_index] = cleaned[index : index + count]
        index += count
    rail_positions = {rail_index: 0 for rail_index in range(rails)}
    decoded_chars: List[str] = []
    for rail_index in pattern:
        chunk = rail_chunks[rail_index]
        pos = rail_positions[rail_index]
        decoded_chars.append(chunk[pos])
        rail_positions[rail_index] += 1
    return "".join(decoded_chars)


def _score_candidate(candidate: str) -> int:
    uppercase = candidate.upper()
    score = 0
    for word in COMMON_PATTERN_WORDS:
        if word and word in uppercase:
            score += len(word) * len(word)
    return score


def _auto_space(text: str) -> str:
    uppercase = text.upper()
    n = len(uppercase)
    dictionary = sorted(set(COMMON_PATTERN_WORDS), key=len, reverse=True)
    result_words: List[str] = []
    i = 0
    while i < n:
        match = None
        for word in dictionary:
            if uppercase.startswith(word, i):
                match = word
                break
        if match:
            result_words.append(match)
            i += len(match)
        else:
            # group consecutive characters that don't match dictionary words
            j = i
            while j < n:
                found = False
                for word in dictionary:
                    if uppercase.startswith(word, j):
                        found = True
                        break
                if found:
                    break
                j += 1
            chunk = uppercase[i:j] if j > i else uppercase[i]
            result_words.append(chunk)
            i = max(j, i + 1)
    collapsed = " ".join(result_words)
    return re.sub(r"\s+", " ", collapsed).strip()


def _format_decoded_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    return cleaned.upper()


@tool
def morse_code_decoder(encrypted_text: str) -> str:
    """Decode Morse code via deterministic mapping."""
    try:
        decoded = _decode_morse(encrypted_text)
        return f"DECODED: {_format_decoded_text(decoded)}"
    except Exception as exc:
        return f"Error decoding Morse code: {exc}"


@tool
def rail_fence_decoder(encrypted_text: str) -> str:
    """Decode Rail Fence cipher by trying common rail counts and scoring results."""
    try:
        cleaned_input = encrypted_text.strip()
        best_candidate = cleaned_input
        best_score = -1
        best_decoded = ""
        for rails in range(2, 7):
            candidate = _rail_fence_decode(cleaned_input, rails)
            score = _score_candidate(candidate)
            if score > best_score:
                best_score = score
                best_candidate = candidate
        spaced = _auto_space(best_candidate)
        formatted = _format_decoded_text(spaced)
        return f"DECODED: {formatted}"
    except Exception as exc:
        return f"Error decoding Rail Fence cipher: {exc}"


def _normalize_polybius_input(encrypted_text: str) -> List[str]:
    cleaned = encrypted_text.replace(",", " ").replace("/", " ")
    cleaned = re.sub(r"[^0-9\s]", " ", cleaned)
    tokens = [token for token in cleaned.split() if token]
    return tokens


@tool
def polybius_square_decoder(encrypted_text: str) -> str:
    """Decode Polybius square coordinates using the standard 5x5 grid."""
    try:
        tokens = _normalize_polybius_input(encrypted_text)
        decoded_chars: List[str] = []
        for token in tokens:
            if token == "24":  # treat 24 as I/J
                decoded_chars.append("I")
                continue
            letter = POLYBIUS_SQUARE.get(token)
            if letter is None:
                raise ValueError(f"Unknown coordinate: {token}")
            decoded_chars.append(letter)
        formatted = _format_decoded_text("".join(decoded_chars))
        return f"DECODED: {formatted}"
    except Exception as exc:
        return f"Error decoding Polybius square: {exc}"
