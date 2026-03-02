import json
import logging
from django.http import JsonResponse
from django.utils.timezone import now

logger = logging.getLogger("security.ratelimit")

def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

def safe_body_preview(request, max_len=1000):
    try:
        body = request.body or b""
        if not body:
            return None
        if len(body) > max_len:
            body = body[:max_len] + b"...(truncated)"
        return body.decode("utf-8", errors="replace")
    except Exception:
        return None

def ratelimit_sinir(request, exception=None):
    ip = get_client_ip(request)
    user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None

    data = {
        "event": "rate_limit_sinir",
        "ts": now().isoformat(),
        "ip": ip,
        "user_id": user.id if user else None,
        "username": getattr(user, "username", None) if user else None,
        "path": request.path,
        "method": request.method,
        "query_string": request.META.get("QUERY_STRING"),
        "referer": request.META.get("HTTP_REFERER"),
        "user_agent": request.META.get("HTTP_USER_AGENT"),
        "accept_language": request.META.get("HTTP_ACCEPT_LANGUAGE"),
        "host": request.get_host(),
        "xff": request.META.get("HTTP_X_FORWARDED_FOR"),
        "real_ip": request.META.get("HTTP_X_REAL_IP"),
        "session_key": getattr(getattr(request, "session", None), "session_key", None),
        "post_keys": list(request.POST.keys()) if request.method in ("POST", "PUT", "PATCH") else None,
        "body_preview": safe_body_preview(request),
    }

    logger.warning(json.dumps(data, ensure_ascii=False))

    return JsonResponse({"detail": "Too many requests"}, status=429)