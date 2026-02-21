import unicodedata
from django.utils.text import slugify

_TURKCE_MAP = {
    "ı": "i", "ğ": "g", "ü": "u",
    "ş": "s", "ö": "o", "ç": "c",
}

def turkce_slugify(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("value must be a string")

    value = unicodedata.normalize("NFKC", value)
    value = value.strip()

    for tr, en in _TURKCE_MAP.items():
        value = value.replace(tr, en).replace(tr.upper(), en)

    return slugify(value)