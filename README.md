# django-routines-tr

Django projeleri için tekrar kullanılabilir middleware, authentication backend ve yardımcı altyapı rutinleri.

Dil yönlendirmesi, admin erişim kontrolü, çok dilli slug yönetimi, e-posta ile giriş, görsel sıkıştırma ve rate limit aşımı loglama gibi tekrar eden altyapı kodlarını azaltmak için tasarlanmış, hafif ve production odaklı yardımcı araçlar içerir.

---

## Özellikler

- Dil duyarlı yönlendirme middleware'i  
- Admin erişim güvenlik middleware'i  
- Çok dilli slug üretimi (LANGUAGES'a göre otomatik slug set etme)  
- Unicode uyumlu çok dilli slug sistemi (Latin dışı alfabeler için otomatik destek)  
- Çok dilli slug yönlendirme yardımcı fonksiyonu  
- Alfabe otomatik tespitli `coklu_slugify` fonksiyonu  
- E-posta ile giriş (authentication backend)  
- Model ImageField görsellerini otomatik WEBP'e çevirme ve sıkıştırma yardımcı fonksiyonu  
- Template'de dinamik görsel optimize etme (template filter) - **Model ve Static dosya desteğiyle**  
- django-ratelimit entegrasyonu ile detaylı rate limit aşımı loglama  

---

## Kurulum

```bash
pip install django-routines-tr
```

Sonra `settings.py` dosyanıza `INSTALLED_APPS` kısmına ekleyin:

```python
INSTALLED_APPS = [
    ...
    'django_routines',
]
```

**Statik dosyalar için gerekli ayarlar (`settings.py`):**

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

**Ana proje `urls.py`'da:**

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django_routines.urls')),  # ← EKLE
]
```

**Statik dosyaları topla:**

```bash
python manage.py collectstatic --noinput
```

Not:  
Görsel sıkıştırma yardımcıları için `Pillow` gereklidir. Paket bağımlılıkları içinde otomatik kurulur.

---

## Middleware Kullanımı

`settings.py` dosyanıza middleware'leri ekleyin:

```python
MIDDLEWARE = [
    ...
    "django_routines.middleware.language_redirect.LanguageRedirectMiddleware",
    "django_routines.middleware.admin_redirect.AdminRedirectMiddleware",
]
```

### LanguageRedirectMiddleware

- URL'leri aktif dile göre otomatik olarak prefixler  
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

Unicode slug kullanılacaksa, Django'nun varsayılan `<slug:slug>` converter'ı yeterli değildir.

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

gibi tüm Unicode slug'lar sorunsuz çalışır.

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

### resim_optimize (Template Filter)

Template'de görüntülenecek resimleri dinamik olarak optimize eder. **Hem Model ImageField'leri hem de Static dosyaları destekler.**

**Özellikler:**

- WEBP formatına çevirip sıkıştırır
- İstenen genişlik ve kalite ayarlarını uygular
- **URL** döndürür; tarayıcı bu URL'e istek attığında görsel o an optimize edilip WEBP olarak servis edilir (1 yıllık `Cache-Control` ile)
- Orijinal dosya boyutu korunur, sadece görüntülenecek versiyon optimize edilir
- Model ImageField ve Static dosyalardan okuyan esnek yapı

**Template'de kullanım:**

```html
{% load resim_optimize %}

<!-- Model ImageField - Default: 2000px genişlik, kalite 100 -->
<img src="{{ product.image|resim_optimize }}" alt="Ürün">

<!-- Model ImageField - Custom: 106px genişlik, kalite 85 -->
<img src="{{ product.image|resim_optimize:'106:85' }}" alt="Ürün">

<!-- Sadece genişlik: kalite varsayılan (100) kalır -->
<img src="{{ product.image|resim_optimize:'200:' }}" alt="Ürün">

<!-- Sadece kalite: genişlik orijinal boyutta kalır, resize yapılmaz -->
<img src="{{ product.image|resim_optimize:':90' }}" alt="Ürün">

<!-- Static dosya -->
<img src="{{ 'images/logo.png'|resim_optimize:'200:90' }}" alt="Logo">

<!-- Static dosya değişkenden -->
{% with static_file='images/banner.jpg' %}
    <img src="{{ static_file|resim_optimize:'1200:85' }}" alt="Banner">
{% endwith %}
```

**Format:** `genişlik:kalite` (ikisi de opsiyonel)

- **genişlik** = Piksel cinsinden (varsayılan: 2000, boş bırakılırsa orijinal boyut korunur, resize yapılmaz)
- **kalite** = 0-100 arasında (varsayılan: 100)

**Console çıktısı (Debug):**

```
✓ Resim: urunler/urun1.jpg | İstenen: 106x85 | Orijinal: (2000, 2000) | Sonuç: 12.45KB
✓ Resim: urunler/urun2.jpg | İstenen: 200x90 | Orijinal: (1500, 1500) | Sonuç: 28.67KB
✓ Resim: images/logo.png | İstenen: 200x90 | Orijinal: (800, 600) | Sonuç: 8.12KB
```

---

#### Nginx Arkasında Kullanım (Production)

`resim_optimize`'nin ürettiği URL'ler gerçek bir dosya uzantısıyla biter (örn. `/optimize/genislik=2000/kalite=85/hero_resimler/bg-img-4-2.webp`). Nginx'in önünde, statik dosyaları uzantıya göre yakalayıp cache header'ı ekleyen tipik bir location bloğu varsa:

```nginx
location ~* ^.+\.(css|js|jpg|jpeg|gif|png|ico|webp|svg|woff2)$ {
    expires max;
}
```

bu blok `proxy_pass` içermediği için `/optimize/...` isteklerini de yakalar, diskte karşılığı olmayan bu "sanal" dosyayı bulamaz ve Django'ya hiç ulaşmadan **404** döner.

**Çözüm:** Bu bloğa `try_files` ile proxy'ye düşen bir fallback ekleyin:

```nginx
location ~* ^.+\.(css|js|jpg|jpeg|gif|png|ico|webp|svg|woff2)$ {
    expires max;
    try_files $uri @proxy;
}

location @proxy {
    proxy_pass http://unix:/path/to/gunicorn.sock;
    proxy_set_header Host $host;
    # ... diğer proxy_set_header'lar, mevcut location / bloğunuzla aynı
}
```

Böylece gerçek static/media dosyaları eskisi gibi doğrudan nginx'ten hızlıca sunulur, `resim_optimize` gibi diskte fiziksel karşılığı olmayan dinamik uzantılı URL'ler otomatik olarak Django'ya proxy'lenir.

---

#### Filter Kodu

```python
from django import template
from PIL import Image
import base64
from io import BytesIO
from django.conf import settings
import os

register = template.Library()

@register.filter
def resim_optimize(image_path, params="2000:85"):
    """
    ImageField için:     {{ product.image|resim_optimize:"106:85" }}
    Static dosyalar için: {{ 'urunler/resim.jpg'|resim_optimize:"106:85" }}
    
    Format: genişlik:kalite
    """
    if not image_path:
        return ''
    
    try:
        width, quality = params.split(':')
        width = int(width)
        quality = int(quality)
    except (ValueError, AttributeError):
        width = 2000
        quality = 85
    
    try:
        # ImageField mi yoksa string path mi kontrolü
        if hasattr(image_path, 'path'):
            # Django ImageField
            dosya_path = image_path.path
            dosya_adi = image_path.name
        else:
            # Static dosya string (örn: 'urunler/resim.jpg')
            dosya_path = os.path.join(settings.STATIC_ROOT, str(image_path))
            dosya_adi = str(image_path)
        
        # Dosya varsa kontrol et
        if not os.path.exists(dosya_path):
            print(f"✗ Dosya bulunamadı: {dosya_path}")
            return ''
        
        img = Image.open(dosya_path)
        orijinal_boyut = img.size
        
        # RGBA varsa RGB'ye çevir
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Yeniden boyutlandır
        img.thumbnail((width, width), Image.Resampling.LANCZOS)
        
        # WEBP'ye kaydet
        output = BytesIO()
        img.save(output, format='WEBP', quality=quality, optimize=True)
        
        # Debug print
        dosya_boyutu_kb = len(output.getvalue()) / 1024
        print(f"✓ Resim: {dosya_adi} | İstenen: {width}x{quality} | Orijinal: {orijinal_boyut} | Sonuç: {dosya_boyutu_kb:.2f}KB")
        
        b64 = base64.b64encode(output.getvalue()).decode()
        return f'data:image/webp;base64,{b64}'
        
    except Exception as e:
        print(f"✗ Resim optimize hatası: {dosya_adi} | {e}")
        return ''
```

---

#### Önemli Not

`collectstatic` komutunu çalıştırmayı unutmayın:

```bash
python manage.py collectstatic --noinput
```

Bu komut, statik dosyaları `STATIC_ROOT`'a kopyalar ve filter'ın çalışmasını sağlar.

---

# Rate Limit Aşımı Loglama

## ratelimit_sinir

`django-ratelimit` ile birlikte çalışır.  
Rate limit aşıldığında (HTTP 429) detaylı güvenlik log'u üretir.

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

`settings.py` dosyanıza aşağıdaki middleware'i ekleyin  
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

Limit aşıldığında otomatik olarak 429 döner ve `ratelimit_sinir` handler'ı çalışarak detaylı güvenlik log'u üretir.

---

### Sunucu Üzerinde Logging İzleme

```bash
sudo journalctl -u gunicorn-ismi -f -o cat | grep rate_limit_sinir
```

---

## Gereksinimler

- Python 3.10+  
- Django 4.2+  

---

## Lisans

Apache Lisansı