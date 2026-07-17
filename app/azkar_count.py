"""Extracts the recommended repetition count (e.g. "1 time", "3 times")
from an azkar entry's free-text "rules" field, which is only ever written
in Bangla in the source data (e.g. "সকাল - সন্ধ্যায় ১ বার করে" or
"সকাল -সন্ধ্যায় তিনবার করে"). Returns a bilingual, human-readable string
or None if no count could be confidently found (some entries -- mostly in
Self-Ruqyah -- are procedural instructions rather than a simple repeat count).
"""
from __future__ import annotations

import re

_BN_DIGITS = "০১২৩৪৫৬৭৮৯"
_BN_TO_LATIN = str.maketrans(_BN_DIGITS, "0123456789")

_WORD_NUMBERS = {
    "এক": 1, "দুই": 2, "তিন": 3, "চার": 4, "পাঁচ": 5, "পাচ": 5,
    "ছয়": 6, "সাত": 7, "আট": 8, "নয়": 9, "দশ": 10,
}

_DIGIT_GROUP_RE = re.compile(r"([০-৯]+(?:\s*[,ও]\s*[০-৯]+)*)\s*বার")
_WORD_RE = re.compile("(" + "|".join(_WORD_NUMBERS) + r")\s*বার")


def extract_count(rules_text: str) -> str | None:
    if not rules_text:
        return None
    m = _DIGIT_GROUP_RE.search(rules_text)
    if m:
        group = m.group(1)
        parts = re.split(r"\s*[,ও]\s*", group)
        latin_parts = [p.translate(_BN_TO_LATIN) for p in parts]
        return ", ".join(latin_parts)
    m = _WORD_RE.search(rules_text)
    if m:
        return str(_WORD_NUMBERS[m.group(1)])
    return None


def format_count(rules_text: str, english: bool) -> str | None:
    count = extract_count(rules_text)
    if count is None:
        return None
    if "," in count:
        return f"{count} {'times' if english else 'বার'}"
    label = "time" if (english and count == "1") else ("times" if english else "বার")
    return f"{count} {label}"
