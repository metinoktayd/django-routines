from django.http import HttpResponse
from django.conf import settings
from django.contrib.staticfiles import finders
from PIL import Image
from io import BytesIO
import os


def resim_optimize_et(istek, resim_yolu, genislik, kalite):
    """
    URL tabanlı resim optimize etme görünümü.
    
    URL Deseni:
        optimize/genislik=(?P<genislik>\d+|orig)/kalite=(?P<kalite>\d+)/(?P<resim_yolu>.+)

    Örnek:
        /optimize/genislik=200/kalite=90/images/logo.png
        /optimize/genislik=106/kalite=85/urunler/urun1.jpg
        /optimize/genislik=orig/kalite=90/urunler/urun1.jpg   # orijinal boyut, resize yok
    """
    try:
        # String türünü kontrol et ve sayıya çevir ("orig" ise resize atlanır)
        genislik = int(genislik) if isinstance(genislik, str) and genislik != 'orig' else genislik
        kalite = int(kalite) if isinstance(kalite, str) else kalite
        
        # Güvenlik: iki nokta path traversal'ını engelle
        if '..' in resim_yolu:
            return HttpResponse("403", status=403)
        
        # Tam dosya yolunu oluştur (önce MEDIA, sonra static finder ile ara)
        tam_yol = os.path.join(settings.MEDIA_ROOT, resim_yolu)
        if not os.path.exists(tam_yol):
            # collectstatic çalıştırılmasa da STATICFILES_DIRS / app static/
            # klasörlerini tarar, bu yüzden STATIC_ROOT'a bağımlı değildir
            tam_yol = finders.find(resim_yolu)

        # Dosya var mı kontrol et
        if not tam_yol or not os.path.exists(tam_yol):
            return HttpResponse("404", status=404)
        
        # Görseli aç
        gorsel = Image.open(tam_yol)
        orijinal_boyut = gorsel.size
        
        # RGBA varsa RGB'ye çevir
        if gorsel.mode in ('RGBA', 'LA', 'P'):
            rgb_gorsel = Image.new('RGB', gorsel.size, (255, 255, 255))
            rgb_gorsel.paste(gorsel, mask=gorsel.split()[-1] if gorsel.mode == 'RGBA' else None)
            gorsel = rgb_gorsel
        
        # Yeniden boyutlandır ("orig" ise orijinal boyut korunur, resize yapılmaz)
        if genislik != 'orig':
            gorsel.thumbnail((genislik, genislik), Image.Resampling.LANCZOS)
        
        # WEBP formatına kaydet
        cikti = BytesIO()
        gorsel.save(cikti, format='WEBP', quality=kalite, optimize=True)
        
        # Hata ayıklama çıktısı
        dosya_boyutu_kb = len(cikti.getvalue()) / 1024
        print(f"[OK] Optimize: {resim_yolu} | İstenen: {genislik}x{kalite} | Orijinal: {orijinal_boyut} | Sonuç: {dosya_boyutu_kb:.2f}KB")
        
        # Yanıt oluştur (1 yıl cache)
        yanitla = HttpResponse(cikti.getvalue(), content_type='image/webp')
        yanitla['Cache-Control'] = 'public, max-age=31536000'
        return yanitla
        
    except ValueError:
        return HttpResponse("400", status=400)
    except Exception as e:
        print(f"[HATA] Optimize hatası: {resim_yolu} | {e}")
        return HttpResponse("500", status=500)