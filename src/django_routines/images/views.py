from django.http import HttpResponse
from django.conf import settings
from PIL import Image
from io import BytesIO
import os


def resim_optimize_et(istek, resim_yolu, genislik, kalite):
    """
    URL tabanlı resim optimize etme görünümü.
    
    URL Deseni:
        optimize/(?P<resim_yolu>.+)/(?P<genislik>\d+)/(?P<kalite>\d+)/
    
    Örnek:
        /optimize/images/logo.png/200/90/
        /optimize/urunler/urun1.jpg/106/85/
    """
    try:
        # String türünü kontrol et ve sayıya çevir
        genislik = int(genislik) if isinstance(genislik, str) else genislik
        kalite = int(kalite) if isinstance(kalite, str) else kalite
        
        # Güvenlik: iki nokta path traversal'ını engelle
        if '..' in resim_yolu:
            return HttpResponse("403", status=403)
        
        # Tam dosya yolunu oluştur
        tam_yol = os.path.join(settings.STATIC_ROOT, resim_yolu)
        
        # Dosya var mı kontrol et
        if not os.path.exists(tam_yol):
            return HttpResponse("404", status=404)
        
        # Görseli aç
        gorsel = Image.open(tam_yol)
        orijinal_boyut = gorsel.size
        
        # RGBA varsa RGB'ye çevir
        if gorsel.mode in ('RGBA', 'LA', 'P'):
            rgb_gorsel = Image.new('RGB', gorsel.size, (255, 255, 255))
            rgb_gorsel.paste(gorsel, mask=gorsel.split()[-1] if gorsel.mode == 'RGBA' else None)
            gorsel = rgb_gorsel
        
        # Yeniden boyutlandır
        gorsel.thumbnail((genislik, genislik), Image.Resampling.LANCZOS)
        
        # WEBP formatına kaydet
        cikti = BytesIO()
        gorsel.save(cikti, format='WEBP', quality=kalite, optimize=True)
        
        # Hata ayıklama çıktısı
        dosya_boyutu_kb = len(cikti.getvalue()) / 1024
        print(f"✓ Optimize: {resim_yolu} | İstenen: {genislik}x{kalite} | Orijinal: {orijinal_boyut} | Sonuç: {dosya_boyutu_kb:.2f}KB")
        
        # Yanıt oluştur (1 yıl cache)
        yanitla = HttpResponse(cikti.getvalue(), content_type='image/webp')
        yanitla['Cache-Control'] = 'public, max-age=31536000'
        return yanitla
        
    except ValueError:
        return HttpResponse("400", status=400)
    except Exception as e:
        print(f"✗ Optimize hatası: {resim_yolu} | {e}")
        return HttpResponse("500", status=500)