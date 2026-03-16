# django-routines-tr

Django projeleri için tekrar kullanılabilir middleware, authentication backend ve yardımcı altyapı rutinleri.

Dil yönlendirmesi, admin erişim kontrolü, çok dilli slug yönetimi, e-posta ile giriş, görsel sıkıştırma ve rate limit aşımı loglama gibi tekrar eden altyapı kodlarını azaltmak için tasarlanmış, hafif ve production odaklı yardımcı araçlar içerir.

---

## Özellikler

- Dil duyarlı yönlendirme middleware’i  
- Admin erişim güvenlik middleware’i  
- Çok dilli slug üretimi (LANGUAGES’a göre otomatik slug set etme)  
- Unicode uyumlu çok dilli slug sistemi (Latin dışı alfabeler için otomatik destek)  
- Çok dilli slug yönlendirme yardımcı fonksiyonu  
- Alfabe otomatik tespitli `coklu_slugify` fonksiyonu  
- E-posta ile giriş (authentication backend)  
- Model ImageField görsellerini otomatik WEBP’e çevirme ve sıkıştırma yardımcı fonksiyonu  
- django-ratelimit entegrasyonu ile detaylı rate limit aşımı loglama  

---

## Kurulum

```bash
pip install django-routines-tr
```

Not:  
Görsel sıkıştırma yardımcıları için `Pillow` gereklidir. Paket bağımlılıkları içinde otomatik kurulur.

---

## Middleware Kullanımı

`settings.py` dosyanıza middleware’leri ekleyin:

```python
MIDDLEWARE = [
    ...
    "django_routines.middleware.language_redirect.LanguageRedirectMiddleware",
    "django_routines.middleware.admin_redirect.AdminRedirectMiddleware",
]
```

### LanguageRedirectMiddleware

- URL’leri aktif dile göre otomatik olarak prefixler  
- Static ve media yollarını hariç tutar  
- `settings.LANGUAGES` ayarını dikkate alır  
- Çift dil prefix oluşumunu engeller  

### AdminRedirectMiddleware

- `/admin/` paneline sadece superuser erişimine izin verir  
- Yetkisiz erişimlerde HTTP 404 döner  
- Admin panelinin ifşa edilmesini azaltmaya yardımcı olur  

---

## Authentication

### EmailBackend

Kullanıcıların e-posta adresi ile giriş yapmasını sağlar.

`settings.py`:

```python
AUTHENTICATION_BACKENDS = [
    "django_routines.backends.email_backend.EmailBackend",
]
```

Örnek kullanım:

```python
from django.contrib.auth import authenticate

user = authenticate(request, username="user@example.com", password="secret")
if user is not None:
    pass
```

Not: Kullanıcı modelinizde `email` alanının unique olması önerilir.

---

# Unicode Uyumlu Slug Sistemi

Yeni sürüm ile birlikte slug sistemi Latin dışı alfabeleri otomatik olarak algılar ve uygun stratejiyi uygular:

- Latin alfabeler → ASCII slug üretir  
- Arapça, Kiril, Yunanca, İbranice, CJK vb. → Unicode slug üretir  
- Slug boş kalırsa fallback üretir  
- `settings.LANGUAGES` değiştiğinde otomatik uyum sağlar  
- Manuel dil listesi tutmaya gerek yoktur  

Bu sayede:

- TR, EN, DE, ES, IT gibi Latin dillerde klasik SEO slug  
- AR gibi dillerde anlamlı Unicode slug  
- Google uyumlu yapı  

---

## coklu_slugify

Türkçe karakter desteği + alfabe otomatik tespiti + Unicode uyumlu slug üretimi sağlar.

```python
from django_routines.i18n.slugify import coklu_slugify

slug = coklu_slugify("İstanbul Şehir Rehberi")
# istanbul-sehir-rehberi

slug_ar = coklu_slugify("دليل خدمات نقل المطار في تركيا")
# دليل-خدمات-نقل-المطار-في-تركيا
```

### Teknik Özellikler

- Türkçe karakter normalizasyonu  
- Unicode NFKC normalizasyonu  
- Latin dışı alfabe otomatik tespiti  
- `allow_unicode=True` otomatik aktivasyonu  
- Boş slug durumunda fallback üretimi  
- Uzunluk kontrolü  

---

## Unicode Slug URL Desteği

Unicode slug kullanılacaksa, Django’nun varsayılan `<slug:slug>` converter’ı yeterli değildir.

Bu nedenle paket içinde `UnicodeSlugConverter` tanımlanmıştır ve `slugify.py` içerisinde yer alır.

### urls.py Kullanımı

```python
from django.urls import path, register_converter
from django_routines.i18n.slugify import UnicodeSlugConverter
from . import views

register_converter(UnicodeSlugConverter, "uslug")

urlpatterns = [
    path("blog/<uslug:slug>/", views.blog_detay, name="blog_detay"),
]
```

Yapılması gereken tek değişiklik:

```
<slug:slug>  →  <uslug:slug>
```

Bu sayede:

- Arapça  
- Rusça  
- Yunanca  
- Çince  
- İbranice  

gibi tüm Unicode slug’lar sorunsuz çalışır.

---

## coklu_dil_slug_uygula

Modelinizde `settings.LANGUAGES` içinde tanımlı dillere göre otomatik slug üretir ve ilgili slug alanlarına set eder.

- Ana alan: `isim` → `slug`  
- Diğer diller: `isim_en` → `slug_en`, `isim_de` → `slug_de`, `isim_ar` → `slug_ar` vb.  
- Model üzerinde ilgili alan yoksa güvenli şekilde atlanır  
- Slug üretimi için dışarıdan bir `slugify_fonksiyonu` alır  
- Unicode alfabeler otomatik desteklenir  

Örnek kullanım (model save içinde):

```python
from django.db import models
from django_routines.i18n.coklu_dil_slug_save import coklu_dil_slug_uygula
from django_routines.i18n.slugify import coklu_slugify

class Blog(models.Model):
    isim = models.CharField(max_length=255)
    # allow_unicode=True → Arapça ve diğer Unicode alfabelerde slug üretimini destekler
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, allow_unicode=True)

    def save(self, *args, **kwargs):
        coklu_dil_slug_uygula(
            nesne=self,
            baslik_alani="isim",
            slug_alani="slug",
            slugify_fonksiyonu=coklu_slugify,
        )
        super().save(*args, **kwargs)
```

---
 
### slugdan_nesne_getir_veya_yonlendir
 
**Slug üzerinden nesneyi bulur** ve gerekirse doğru dil slug'ına yönlendirir.
 
Hangi dilde yazıldığı bilinmeyen bir slug ile geldiğinizde, tüm dil alanlarında arama yaparak nesneyi bulur.  
Aktif dildeki slug farklıysa yönlendirme döndürür; doğruysa nesneyi döndürür.
 
Kullanım senaryosu: Standart slug tabanlı URL yapısı. Slug'ı siz çekmiyorsunuz, URL'den doğrudan geliyor.
 
```python
from django_routines.i18n.slug_redirect import slugdan_nesne_getir_veya_yonlendir
 
def makale_detay(request, slug):
    nesne, redirect = slugdan_nesne_getir_veya_yonlendir(
        model=Makale,
        mevcut_slug=slug,
        url_adi="makale-detay",
    )
    if redirect:
        return redirect
 
    return render(request, "makale_detay.html", {"makale": nesne})
```

> Redirect varsa view içinde **önce redirect döndürülmelidir.**
 
---


# Rate Limit Aşımı Loglama

## ratelimit_sinir

`django-ratelimit` ile birlikte çalışır.  
Rate limit aşıldığında (HTTP 429) detaylı güvenlik log’u üretir.

Loglanan bilgiler:

- Client IP (X-Forwarded-For destekli)
- Kullanıcı ID ve username (authenticated ise)
- Path ve HTTP method
- Query string
- Referer
- User-Agent
- Accept-Language
- Host
- Session key
- POST key listesi
- Truncate edilmiş body preview

---

## Kurulum

### 1) Middleware Ekleyin

`settings.py` dosyanıza aşağıdaki middleware’i ekleyin  
(Genellikle listenin alt kısmında olması önerilir):

```python
MIDDLEWARE = [
    ...
    "django_ratelimit.middleware.RatelimitMiddleware",
]
```

---

### 2) Rate Limit Handler Tanımlayın

```python
RATELIMIT_VIEW = "django_routines.ratelimit_sinir.ratelimit_sinir"
```

---

### 3) Cache Ayarı (Production Önerisi)

`django-ratelimit` cache tabanlı çalışır.  
Multi-worker production ortamda `LocMemCache` önerilmez.

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}
```

Redis veya Memcached gibi paylaşımlı cache kullanılması önerilir.

---

### 4) View Üzerinde Kullanım

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key="ip", rate="3/m", method="POST", block=True)
def iletisim(request):
    ...
```

Limit aşıldığında otomatik olarak 429 döner ve `ratelimit_sinir` handler’ı çalışarak detaylı güvenlik log'u üretir.

---

### Sunucu Üzerinde Logging İzleme

```bash
sudo journalctl -u gunicorn-ismi -f -o cat | grep rate_limit_sinir
```

---

## Görsel Sıkıştırma

### resim_sikistir

Model üzerindeki bir `ImageField` alanını:

- Eski görsel değiştiyse `eski_<upload_to>/` klasörüne taşır  
- WEBP formatına çevirir  
- `max_kenar` ile en büyük boyutu sınırlar  
- `max_kb` altına düşene kadar kaliteyi optimize eder  

Örnek kullanım:

```python
from django.db import models
from django_routines.images.compress import resim_sikistir

class Urun(models.Model):
    resim = models.ImageField(upload_to="urun_resimleri/", blank=True, null=True)

    def save(self, *args, **kwargs):
        resim_sikistir(self, "resim", dosya_adi="urun", max_kb=200, max_kenar=1200)
        super().save(*args, **kwargs)
```

---

## Gereksinimler

- Python 3.10+  
- Django 4.2+  

---

## Lisans

Apache Lisansı