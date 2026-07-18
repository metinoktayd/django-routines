from django import template
from django.urls import reverse
from django.conf import settings

register = template.Library()

@register.filter
def resim_optimize(resim_yolu, parametreler="2000:100"):
    """
    URL tabanlı resim optimize etme filtresi.

    Kullanım:
        {{ product.image|resim_optimize }}             # 2000px, kalite 100
        {{ product.image|resim_optimize:"106:85" }}     # 106px, kalite 85
        {{ product.image|resim_optimize:"200:" }}       # 200px, kalite varsayılan (100)
        {{ product.image|resim_optimize:":90" }}        # orijinal genişlik, kalite 90
        {{ 'images/logo.png'|resim_optimize:"200:90" }}

    Format: genişlik:kalite (ikisi de opsiyonel; boş bırakılan taraf
    genişlik için orijinal boyutu, kalite için 100'ü kullanır)
    """
    if not resim_yolu:
        return ''

    try:
        genislik_ham, _, kalite_ham = parametreler.partition(':')
    except AttributeError:
        genislik_ham, kalite_ham = '', ''

    genislik_ham = genislik_ham.strip()
    kalite_ham = kalite_ham.strip()

    genislik = int(genislik_ham) if genislik_ham.isdigit() else 'orig'
    kalite = int(kalite_ham) if kalite_ham.isdigit() else 100
    
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
        print(f"[HATA] Resim URL oluşturma hatası: {resim_yolu} | {e}")
        return ''