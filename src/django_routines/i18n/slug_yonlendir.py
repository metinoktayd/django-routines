from __future__ import annotations

from typing import Any, Iterable, Tuple, Type, TypeVar

from django.conf import settings
from django.db.models import Model, Q, QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import get_language

ModelT = TypeVar("ModelT", bound=Model)


def aktif_dili_al() -> str:
    """
    Django'nun aktif dilini (örn: 'tr', 'en') döndürür.
    """
    return (get_language() or "").lower().split("-")[0]


def dogru_i18n_slug_icin_yonlendir(
    *,
    nesne: Any,
    mevcut_slug: str,
    url_adi: str,
    slug_parametresi: str = "slug",
    slug_alan_on_eki: str = "slug_",
    ekstra_parametreler: dict[str, Any] | None = None,
):
    """
    Nesnenin aktif dile ait slug alanını kontrol eder.
    Eğer URL'deki slug yanlışsa doğru slug'a redirect döndürür.
    Doğruysa None döner.
    """

    dil = aktif_dili_al()
    alan_adi = f"{slug_alan_on_eki}{dil}"
    dogru_slug = getattr(nesne, alan_adi, None)

    if dogru_slug and mevcut_slug != dogru_slug:
        parametreler: dict[str, Any] = {slug_parametresi: dogru_slug}

        if ekstra_parametreler:
            parametreler.update(ekstra_parametreler)

        return HttpResponseRedirect(
            reverse(url_adi, kwargs=parametreler)
        )

    return None


def slugdan_nesne_getir_veya_yonlendir(
    *,
    model: Type[ModelT],
    mevcut_slug: str,
    url_adi: str,
    temel_sorgu: QuerySet[ModelT] | None = None,
    diller: Iterable[Tuple[str, str]] | None = None,
    slug_parametresi: str = "slug",
    slug_alan_on_eki: str = "slug_",
    ekstra_parametreler: dict[str, Any] | None = None,
    ertelenecek_alanlar: tuple[str, ...] = (),
) -> tuple[ModelT | None, HttpResponseRedirect | None]:
    """
    Verilen slug hangi dilde olursa olsun nesneyi bulur.
    Aktif dildeki slug farklıysa doğru slug'a yönlendirme döndürür.

    Dönüş:
        (nesne, redirect)

    redirect varsa view içinde önce redirect döndürülmelidir.
    """

    sorgu = temel_sorgu if temel_sorgu is not None else model._default_manager.all()

    if ertelenecek_alanlar:
        sorgu = sorgu.defer(*ertelenecek_alanlar)

    aktif_diller = diller if diller is not None else settings.LANGUAGES

    kosul = Q()

    for kod, _ in aktif_diller:
        kosul |= Q(**{f"{slug_alan_on_eki}{kod}": mevcut_slug})

    nesne = get_object_or_404(sorgu.filter(kosul))

    redirect = dogru_i18n_slug_icin_yonlendir(
        nesne=nesne,
        mevcut_slug=mevcut_slug,
        url_adi=url_adi,
        slug_parametresi=slug_parametresi,
        slug_alan_on_eki=slug_alan_on_eki,
        ekstra_parametreler=ekstra_parametreler,
    )

    if redirect:
        return None, redirect

    return nesne, None