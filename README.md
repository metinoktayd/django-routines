# django-routines-tr

Django projeleri için tekrar kullanılabilir middleware, authentication backend ve altyapı rutinleri.

Dil yönlendirmesi, admin erişim kontrolü, çok dilli slug yönetimi ve e-posta ile giriş gibi tekrar eden altyapı kodlarını ortadan kaldırmak için tasarlanmış, hafif ve production odaklı yardımcı araçlar içerir.

---

## Özellikler

- Dil duyarlı yönlendirme middleware’i  
- Admin erişim güvenlik middleware’i  
- Çok dilli slug yönlendirme yardımcı fonksiyonu  
- Türkçe karakter uyumlu slugify fonksiyonu  
- E-posta ile giriş (authentication backend)  

---

## Kurulum

```bash
pip install django-routines-tr
```

---

## Kullanım

## Middleware Eklemek

`settings.py` dosyanıza middleware’leri ekleyin:

```python
MIDDLEWARE = [
    ...
    "django_routines.middleware.language_redirect.LanguageRedirectMiddleware",
    "django_routines.middleware.admin_redirect.AdminRedirectMiddleware",
]
```

---

## Middleware Detayları

### LanguageRedirectMiddleware

- URL’leri aktif dile göre otomatik olarak prefixler  
- Static ve media yollarını hariç tutar  
- `settings.LANGUAGES` ayarını dikkate alır  
- Çift dil prefix oluşumunu engeller  

---

### AdminRedirectMiddleware

- `/admin/` paneline sadece superuser erişimine izin verir  
- Yetkisiz erişimlerde HTTP 404 döner  
- Admin panelinin ifşa edilmesini azaltmaya yardımcı olur  

---

## Authentication

### EmailBackend

Kullanıcıların e-posta adresi ile giriş yapmasını sağlar.

### Ayar

`settings.py` dosyanıza ekleyin:

```python
AUTHENTICATION_BACKENDS = [
    "django_routines.auth.email_backend.EmailBackend",
]
```

Bu backend:

- `username` parametresi yerine e-posta alanı üzerinden kullanıcıyı bulur  
- Şifre doğrulamasını Django’nun standart mekanizması ile yapar  
- `is_active` kontrolünü korur  

### Örnek Kullanım

```python
from django.contrib.auth import authenticate

user = authenticate(request, username="user@example.com", password="secret")

if user is not None:
    # giriş başarılı
    pass
```

Not: Kullanıcı modelinizde `email` alanı unique olmalıdır.

---

## Yardımcı Fonksiyonlar

### turkce_slugify

Türkçe karakterleri ASCII uyumlu karşılıklarına çevirir ve ardından Django’nun `slugify` fonksiyonunu uygular.

```python
from django_routines import turkce_slugify

slug = turkce_slugify("İstanbul Şehir Rehberi")
# Çıktı: istanbul-sehir-rehberi
```

---

### redirect_to_correct_i18n_slug

Aktif dile göre doğru slug alanını kontrol eder ve gerekirse doğru slug’a yönlendirme yapar.

```python
from django_routines import redirect_to_correct_i18n_slug

response = redirect_to_correct_i18n_slug(
    obj=article,
    current_slug=slug,
    url_name="article_detail",
)

if response:
    return response
```

---

## Gereksinimler

- Python 3.10+
- Django 4.2+

---

## Lisans

Apache Lisansı