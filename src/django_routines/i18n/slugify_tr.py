from django.utils.text import slugify

_TURKCE_MAP = {
    "ı": "i", "İ": "i",
    "ğ": "g", "Ğ": "g",
    "ü": "u", "Ü": "u",
    "ş": "s", "Ş": "s",
    "ö": "o", "Ö": "o",
    "ç": "c", "Ç": "c",
}

def turkce_slugify(value: str) -> str:
    for tr, en in _TURKCE_MAP.items():
        value = value.replace(tr, en)
    return slugify(value)