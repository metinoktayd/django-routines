import re
import unicodedata
from uuid import uuid4
from django.utils.text import slugify
from unidecode import unidecode

_TURKCE_MAP = {
    "ı": "i", "ğ": "g", "ü": "u",
    "ş": "s", "ö": "o", "ç": "c",
}

class UnicodeSlugConverter:
    # Slash hariç her şeyi kabul eder
    regex = r"[^/]+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value

def _contains_non_latin(text: str) -> bool:
    """
    Metinde Latin alfabesi dışı harf var mı?
    (Arabic, Cyrillic, Greek, Hebrew, CJK vs.)
    """
    for ch in text:
        name = unicodedata.name(ch, "")
        if "LATIN" in name:
            continue
        # Harf olup LATIN değilse -> farklı alfabe
        if ch.isalpha():
            return True
    return False


def coklu_slugify(value: str, *, fallback_prefix: str = "item", max_length: int | None = 240) -> str:
    if not isinstance(value, str):
        raise TypeError("value must be a string")

    value = unicodedata.normalize("NFKC", value).strip()

    # Türkçe düzeltme
    for tr, en in _TURKCE_MAP.items():
        value = value.replace(tr, en).replace(tr.upper(), en)

    # Alfabe tespiti
    if _contains_non_latin(value):
        # Unicode slug (Arapça, Rusça, Yunanca vs.)
        s = slugify(value, allow_unicode=True)
    else:
        # Latin temelli diller → ASCII slug
        try:
            value2 = unidecode(value)
        except Exception:
            value2 = value
        s = slugify(value2, allow_unicode=False)
    if not s:
        s = f"{fallback_prefix}-{uuid4().hex[:8]}"
    if max_length and len(s) > max_length:
        s = s[:max_length].rstrip("-")

    return s