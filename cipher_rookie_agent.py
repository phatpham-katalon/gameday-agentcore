# Copyright 2025 Amazon.com and its affiliates; all rights reserved.
# This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

"""
Cipher Rookie Agent - Basic Substitution Ciphers
Deterministic decoders for Caesar, Atbash, and monoalphabetic substitution ciphers.
"""

import math
import random
import re
import string
from typing import Dict, List

from strands import tool

LETTERS = string.ascii_uppercase
ETAOIN = "ETAOINSHRDLCUMWFGYPBVKJXQZ"

COMMON_WORDS = {
    "THE",
    "AND",
    "THIS",
    "THAT",
    "FOR",
    "OF",
    "TO",
    "IN",
    "ON",
    "WITH",
    "LLAMA",
    "LLAMAS",
    "UNICORN",
    "UNICORNS",
    "MISSION",
    "SECRET",
    "MESSAGE",
    "BASE",
    "MOUNTAIN",
    "ATTACK",
    "RENDEZVOUS",
    "AGENT",
    "HIDDEN",
    "DANGER",
    "EVIL",
    "CODE",
    "ALERT",
    "UNITS",
    "GUARD",
    "EAST",
    "WEST",
    "NORTH",
    "SOUTH",
    "HILLS",
    "SUMMIT",
    "THEIR",
    "FROM",
    "WHEN",
    "WHERE",
    "ARE",
    "IS",
}


def _format_decoded(result: str, label: str = "DECODED") -> str:
    cleaned = re.sub(r"\s+", " ", result.strip())
    return f"{label}: {cleaned.upper()}"


def _score_plaintext(text: str) -> float:
    uppercase = text.upper()
    words = re.findall(r"[A-Z]+", uppercase)
    hits = sum(1 for word in words if word in COMMON_WORDS)
    vowel_ratio = sum(1 for c in uppercase if c in "AEIOU") / max(len(uppercase), 1)
    space_bonus = uppercase.count(" ")
    penalty = sum(1 for c in uppercase if c in "QXZJ") * 0.5
    return hits * 20 + vowel_ratio * 10 + space_bonus - penalty


def _shift_character(ch: str, shift: int) -> str:
    if ch.isalpha():
        alphabet = string.ascii_uppercase if ch.isupper() else string.ascii_lowercase
        idx = alphabet.index(ch)
        return alphabet[(idx + shift) % 26]
    return ch


def _decode_caesar(text: str, shift: int) -> str:
    return "".join(_shift_character(ch, shift) for ch in text)


@tool
def caesar_cipher_decoder(encrypted_text: str) -> str:
    """Brute-force all shifts and choose the highest-scoring plaintext."""
    best_plain = encrypted_text
    best_score = -math.inf
    for shift in range(1, 26):
        candidate = _decode_caesar(encrypted_text, shift)
        score = _score_plaintext(candidate)
        if score > best_score:
            best_score = score
            best_plain = candidate
    return _format_decoded(best_plain, label="DECODED")


@tool
def atbash_cipher_decoder(encrypted_text: str) -> str:
    """Apply alphabet mirroring (A↔Z, B↔Y, ...)."""
    def decode_char(ch: str) -> str:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            mirrored = 25 - (ord(ch.upper()) - ord("A"))
            return chr(base + mirrored)
        return ch

    plaintext = "".join(decode_char(ch) for ch in encrypted_text)
    return _format_decoded(plaintext, label="DECODED")


def _build_initial_key(ciphertext: str) -> List[str]:
    uppercase = [ch for ch in ciphertext.upper() if ch in LETTERS]
    counts: Dict[str, int] = {letter: 0 for letter in LETTERS}
    for ch in uppercase:
        counts[ch] += 1
    ordered_cipher_letters = sorted(LETTERS, key=lambda letter: counts[letter], reverse=True)
    plaintext_order = list(ETAOIN) + [letter for letter in LETTERS if letter not in ETAOIN]
    key = [""] * 26
    used_plain_letters = set()
    for cipher_letter, plain_letter in zip(ordered_cipher_letters, plaintext_order):
        key_index = LETTERS.index(cipher_letter)
        key[key_index] = plain_letter
        used_plain_letters.add(plain_letter)
    remaining_plain_letters = [letter for letter in LETTERS if letter not in used_plain_letters]
    for idx in range(26):
        if key[idx] == "":
            key[idx] = remaining_plain_letters.pop(0)
    return key


def _decrypt_with_key(key: List[str], text: str) -> str:
    table = {cipher: plain for cipher, plain in zip(LETTERS, key)}
    result_chars: List[str] = []
    for ch in text:
        upper = ch.upper()
        if upper in table:
            decoded = table[upper]
            result_chars.append(decoded if ch.isupper() else decoded.lower())
        else:
            result_chars.append(ch)
    return "".join(result_chars)


def _swap_key_positions(key: List[str], i: int, j: int) -> List[str]:
    new_key = key[:]
    new_key[i], new_key[j] = new_key[j], new_key[i]
    return new_key


def _hill_climb(ciphertext: str, iterations: int = 2000, seed: int = 0) -> str:
    rng = random.Random((hash(ciphertext) + seed) & 0xFFFFFFFF)
    key = _build_initial_key(ciphertext)
    best_plain = _decrypt_with_key(key, ciphertext)
    best_score = _score_plaintext(best_plain)
    for _ in range(iterations):
        i, j = rng.sample(range(26), 2)
        swapped_key = _swap_key_positions(key, i, j)
        candidate_plain = _decrypt_with_key(swapped_key, ciphertext)
        candidate_score = _score_plaintext(candidate_plain)
        if candidate_score > best_score:
            key = swapped_key
            best_plain = candidate_plain
            best_score = candidate_score
    return best_plain


@tool
def simple_substitution_decoder(encrypted_text: str) -> str:
    """Crack monoalphabetic substitution via frequency scoring and hill climbing."""
    best_plain = encrypted_text
    best_score = -math.inf
    for attempt in range(10):
        candidate = _hill_climb(encrypted_text, iterations=2000, seed=attempt)
        score = _score_plaintext(candidate)
        if score > best_score:
            best_score = score
            best_plain = candidate
    return _format_decoded(best_plain, label="DECODED")
