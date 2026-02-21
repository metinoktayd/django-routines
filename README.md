# django-routines-tr

Django projeleri için tekrar kullanılabilir middleware, authentication backend ve yardımcı altyapı rutinleri.

Dil yönlendirmesi, admin erişim kontrolü, çok dilli slug yönetimi, e-posta ile giriş ve görsel sıkıştırma gibi tekrar eden altyapı kodlarını azaltmak için tasarlanmış, hafif ve production odaklı yardımcı araçlar içerir.

---

## Özellikler

- Dil duyarlı yönlendirme middleware’i  
- Admin erişim güvenlik middleware’i  
- Çok dilli slug yönlendirme yardımcı fonksiyonu  
- Türkçe karakter uyumlu slugify fonksiyonu  
- E-posta ile giriş (authentication backend)  
- Model ImageField görsellerini otomatik WEBP’e çevirme ve sıkıştırma yardımcı fonksiyonu  

---

## Kurulum

```bash
pip install django-routines-tr
```

Not: Görsel sıkıştırma yardımcıları için `Pillow` gereklidir. Paket bağımlılıkları içinde otomatik kurulur.

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

Örnek:

```python
from django.contrib.auth import authenticate

user = authenticate(request, username="user@example.com", password="secret")
if user is not None:
    pass
```

Not: Kullanıcı modelinizde `email` alanının unique olması önerilir.

---

## Yardımcı Fonksiyonlar

### turkce_slugify

Türkçe karakterleri ASCII uyumlu karşılıklarına çevirir ve ardından Django’nun `slugify` fonksiyonunu uygular.

```python
from django_routines.i18n.slugify import turkce_slugify

slug = turkce_slugify("İstanbul Şehir Rehberi")
# Çıktı: istanbul-sehir-rehberi
```

---

### redirect_to_correct_i18n_slug

Aktif dile göre doğru slug alanını kontrol eder ve gerekirse doğru slug’a yönlendirme yapar.

```python
from django_routines.i18n.slug_redirect import redirect_to_correct_i18n_slug

response = redirect_to_correct_i18n_slug(
    obj=article,
    current_slug=slug,
    url_name="article_detail",
)

if response:
    return response
```

---

## Görsel Sıkıştırma

### resim_sikistir

Model üzerindeki bir `ImageField` alanını:

- Eski görsel değiştiyse `eski_<upload_to>/` klasörüne taşır (local ise taşıma, remote ise copy+delete)  
- Görseli WEBP formatına çevirir  
- `max_kenar` ile en büyük kenarı küçültür  
- `max_kb` hedef boyutuna inene kadar kaliteyi düşürür  

Örnek kullanım (model save içinde):

```python
from django.db import models
from django_routines.images.compress import resim_sikistir

class Urun(models.Model):
    resim = models.ImageField(upload_to="urun_resimleri/", blank=True, null=True)

    def save(self, *args, **kwargs):
        # save öncesi alanın file'ı set edildiyse sıkıştır
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