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

        # 1. KONTROL: URL zaten geçerli bir dil koduyla mı başlıyor?
        # Sonda slash olmasa bile (örn: /tr veya /tr/admin) yakalamak için f"/{lang}" kontrolü yapıyoruz
        for lang, _ in settings.LANGUAGES:
            if path == f"/{lang}" or path.startswith(f"/{lang}/"):
                
                # KRİTİK EKLEME: Eğer URL dil koduyla başlıyor ama /tr/admin gibi sonda slash yoksa
                # APPEND_SLASH mantığını DEBUG moduna bırakmadan doğrudan burada tetikliyoruz.
                if not path.endswith('/') and settings.APPEND_SLASH:
                    # Query stringleri (?page=1 vb.) kaybetmemek için request.GET'i de ekliyoruz
                    query_string = f"?{request.META['QUERY_STRING']}" if request.META.get('QUERY_STRING') else ""
                    return HttpResponseRedirect(f"{path}/{query_string}")
                    
                return self.get_response(request)

        # 2. KONTROL: Eğer URL'de hiç dil kodu yoksa (örn: direkt /admin yazıldıysa)
        # Tarayıcı dilini alıp yönlendiriyoruz
        lang = translation.get_language_from_request(request, check_path=False)
        if lang in dict(settings.LANGUAGES):
            query_string = f"?{request.META['QUERY_STRING']}" if request.META.get('QUERY_STRING') else ""
            return HttpResponseRedirect(f"/{lang}{path}{query_string}")

        return self.get_response(request)