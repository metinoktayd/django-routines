from django.conf import settings


def coklu_dil_slug_uygula(nesne, baslik_alani="isim", slug_alani="slug", slugify_fonksiyonu=None):
    if not slugify_fonksiyonu:
        raise ValueError("slugify_fonksiyonu parametresi zorunludur")

    # Ana dil (varsayılan alan)
    ana_baslik = getattr(nesne, baslik_alani, None)
    if ana_baslik:
        setattr(nesne, slug_alani, slugify_fonksiyonu(ana_baslik))

    # Diğer diller
    for dil_kodu, _ in getattr(settings, "LANGUAGES", []):
        if dil_kodu == "tr":
            continue

        baslik_attr = f"{baslik_alani}_{dil_kodu}"
        slug_attr = f"{slug_alani}_{dil_kodu}"

        if hasattr(nesne, baslik_attr) and hasattr(nesne, slug_attr):
            deger = getattr(nesne, baslik_attr)
            if deger:
                setattr(nesne, slug_attr, slugify_fonksiyonu(deger))