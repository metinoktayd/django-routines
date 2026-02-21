from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation

class LanguageRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        exempt_paths = (
            settings.STATIC_URL,
            settings.MEDIA_URL,
            "/set-language/",
            "/i18n/",
        )
        if path.startswith(exempt_paths):
            return self.get_response(request)

        if path.startswith(tuple(f"/{lang}/" for lang, _ in settings.LANGUAGES)):
            return self.get_response(request)

        lang = translation.get_language_from_request(request, check_path=False)
        if lang in dict(settings.LANGUAGES):
            return HttpResponseRedirect(f"/{lang}{path}")

        return self.get_response(request)