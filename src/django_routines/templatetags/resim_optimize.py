from django import template
from django.urls import reverse
from django.conf import settings

kayit = template.Library()

@kayit.filter
def resim_optimize(resim_yolu, parametreler="2000:85"):
    """
    URL tabanlı resim optimize etme filtresi.
    
    Kullanım:
        {{ product.image|resim_optimize }}
        {{ product.image|resim_optimize:"106:85" }}
        {{ 'images/logo.png'|resim_optimize:"200:90" }}
    
    Format: genişlik:kalite
    """
    if not resim_yolu:
        return ''
    
    try:
        genislik, kalite = parametreler.split(':')
        genislik = int(genislik)
        kalite = int(kalite)
    except (ValueError, AttributeError):
        genislik = 2000
        kalite = 85
    
    try:
        # ImageField mi yoksa string yolu mu kontrol et
        if hasattr(resim_yolu, 'name'):
            # Django ImageField
            yol_metni = resim_yolu.name
        else:
            # String yolu
            yol_metni = str(resim_yolu)
        
        # Optimize görünümüne yönlendir
        optimize_url = reverse(
            'django_routines:resim_optimize_et',
            kwargs={
                'resim_yolu': yol_metni,
                'genislik': genislik,
                'kalite': kalite
            }
        )
        
        return optimize_url
        
    except Exception as e:
        print(f"✗ Resim URL oluşturma hatası: {resim_yolu} | {e}")
        return ''