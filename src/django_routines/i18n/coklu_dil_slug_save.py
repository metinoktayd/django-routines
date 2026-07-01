import random
from django.conf import settings

def _unique_slug_uret(nesne, slug_degeri, slug_alani):
    if not slug_degeri:
        return slug_degeri

    model = nesne.__class__
    field = nesne._meta.get_field(slug_alani)
    max_len = getattr(field, "max_length", 255) or 255

    qs = model.objects.all()
    if nesne.pk:
        qs = qs.exclude(pk=nesne.pk)

    # İlk slug boşta ise direkt kullan
    if not qs.filter(**{slug_alani: slug_degeri}).exists():
        return slug_degeri

    # Sonuna -1234 ekleneceği için 5 karakter ayır
    suffix_len = 5
    base_max_len = max_len - suffix_len
    base_slug = slug_degeri[:base_max_len].rstrip("-")

    while True:
        rastgele_sayi = random.randint(1000, 9999)
        aday_slug = f"{base_slug}-{rastgele_sayi}"

        if not qs.filter(**{slug_alani: aday_slug}).exists():
            return aday_slug


def coklu_dil_slug_uygula(nesne, baslik_alani="isim", slug_alani="slug", slugify_fonksiyonu=None):
    if not slugify_fonksiyonu:
        raise ValueError("slugify_fonksiyonu parametresi zorunludur")

    # Ana dil (varsayılan alan)
    ana_baslik = getattr(nesne, baslik_alani, None)
    if ana_baslik:
        ana_slug = slugify_fonksiyonu(ana_baslik)
        ana_slug = _unique_slug_uret(nesne, ana_slug, slug_alani)
        setattr(nesne, slug_alani, ana_slug)

    # Diğer diller
    for dil_kodu, _ in getattr(settings, "LANGUAGES", []):
        if dil_kodu == "tr":
            continue

        baslik_attr = f"{baslik_alani}_{dil_kodu}"
        slug_attr = f"{slug_alani}_{dil_kodu}"

        if hasattr(nesne, baslik_attr) and hasattr(nesne, slug_attr):
            deger = getattr(nesne, baslik_attr)
            if deger:
                slug_degeri = slugify_fonksiyonu(deger)
                slug_degeri = _unique_slug_uret(nesne, slug_degeri, slug_attr)
                setattr(nesne, slug_attr, slug_degeri)