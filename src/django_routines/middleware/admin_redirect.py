from django.http import Http404

class AdminRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        supported_langs = ["tr", "en"]

        is_admin_path = any(path.startswith(f"/{lang}/admin/") for lang in supported_langs)

        if is_admin_path:
            if (not hasattr(request, "user")
                or not request.user.is_authenticated
                or not request.user.is_superuser):
                raise Http404("Sayfa bulunamadı.")

        return self.get_response(request)