import os
from io import BytesIO
from pathlib import Path
from django.core.files.base import ContentFile
from PIL import Image, ImageOps
from django.core.files.storage import default_storage

def resim_sikistir(model_ornek, alan_adi, dosya_adi="resim", max_kb=200, max_kenar=1200, kalite_adimlari=(82,75,68,60,52,45,38,32,28,25), method=4, eski_klasor_prefix="eski_"):
    image_field = getattr(model_ornek, alan_adi, None)
    if not image_field or not getattr(image_field, "file", None):
        return False

    try:
        # 1) Eğer kayıt güncelleniyorsa ve resim değiştiyse eskiyi "eski_<upload_to>" klasörüne taşı
        if getattr(model_ornek, "pk", None):
            try:
                eski_kayit = model_ornek.__class__.objects.only(alan_adi).get(pk=model_ornek.pk)
                eski_field = getattr(eski_kayit, alan_adi, None)
                eski_ad = getattr(eski_field, "name", "") or ""
                yeni_ad = getattr(image_field, "name", "") or ""

                if eski_ad and eski_ad != yeni_ad and default_storage.exists(eski_ad):
                    # eski_ad örn: kullanici_resimleri/abc.jpg
                    upload_klasoru = os.path.dirname(eski_ad)  # kullanici_resimleri
                    eski_dosya_adi = os.path.basename(eski_ad) # abc.jpg
                    hedef_klasor = f"{eski_klasor_prefix}{upload_klasoru}" if upload_klasoru else eski_klasor_prefix.rstrip("_")
                    hedef_ad = os.path.join(hedef_klasor, eski_dosya_adi)

                    # Çakışma olursa dosya adının sonuna _1, _2 ekle (isim değiştirmek istemiyorsunuz ama çakışma yönetmek şart)
                    if default_storage.exists(hedef_ad):
                        ad, ext = os.path.splitext(eski_dosya_adi)
                        i = 1
                        while True:
                            hedef_ad = os.path.join(hedef_klasor, f"{ad}_{i}{ext}")
                            if not default_storage.exists(hedef_ad):
                                break
                            i += 1

                    # Local storage: taşımaya çalış, olmazsa kopyala-sil
                    try:
                        src_path = default_storage.path(eski_ad)
                        dst_path = default_storage.path(hedef_ad)
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        os.replace(src_path, dst_path)  # taşır
                    except Exception:
                        # S3 vb: copy+delete
                        with default_storage.open(eski_ad, "rb") as f:
                            default_storage.save(hedef_ad, f)
                        default_storage.delete(eski_ad)

            except model_ornek.__class__.DoesNotExist:
                pass

        # 2) Zaten webp ise tekrar sıkıştırma yapma
        mevcut_isim = (image_field.name or "").lower()
        if mevcut_isim.endswith(".webp"):
            return True

        # 3) WEBP’e çevir ve hedef boyuta indir
        dosya = image_field.file
        dosya.seek(0)
        resim = Image.open(dosya)
        resim = ImageOps.exif_transpose(resim)

        if resim.mode not in ("RGB", "RGBA"):
            resim = resim.convert("RGB")

        genislik, yukseklik = resim.size
        en_buyuk = max(genislik, yukseklik)
        if en_buyuk > max_kenar:
            oran = max_kenar / float(en_buyuk)
            resim = resim.resize((int(genislik * oran), int(yukseklik * oran)), Image.LANCZOS)

        def webp_aktar(img, kalite):
            buffer = BytesIO()
            img.save(buffer, format="WEBP", quality=kalite, method=method)
            return buffer

        icerik = None
        for kalite in kalite_adimlari:
            buffer = webp_aktar(resim, kalite)
            if (buffer.tell() / 1024) <= max_kb:
                icerik = ContentFile(buffer.getvalue())
                break

        if icerik is None:
            resim = resim.resize((max(1, int(resim.size[0]*0.8)), max(1, int(resim.size[1]*0.8))), Image.LANCZOS)
            buffer = webp_aktar(resim, kalite_adimlari[-1])
            icerik = ContentFile(buffer.getvalue())

        temiz_ad = Path(dosya_adi).stem or "resim"
        image_field.save(f"{temiz_ad}.webp", icerik, save=False)
        return True

    except Exception:
        return False