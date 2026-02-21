from __future__ import annotations

from typing import Any
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import get_language

def redirect_to_correct_i18n_slug(
    *,
    obj: Any,
    current_slug: str,
    url_name: str,
    slug_kwarg: str = "slug",
    slug_field_prefix: str = "slug_",
    extra_kwargs: dict[str, Any] | None = None,
):
    lang = (get_language() or "").lower().split("-")[0]
    field_name = f"{slug_field_prefix}{lang}"
    correct_slug = getattr(obj, field_name, None)

    if correct_slug and current_slug != correct_slug:
        kwargs: dict[str, Any] = {slug_kwarg: correct_slug}
        if extra_kwargs:
            kwargs.update(extra_kwargs)
        return HttpResponseRedirect(reverse(url_name, kwargs=kwargs))

    return None