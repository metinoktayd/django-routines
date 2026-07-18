from django import template
from PIL import Image
import base64
from io import BytesIO

register = template.Library()

@register.filter
def resim_optimize(image_field, params="2000:85"):
    """
    {{ product.image|optimize_image:"106:85" }}
    Format: genişlik:kalite
    """
    if not image_field:
        return ''
    
    try:
        width, quality = params.split(':')
        width = int(width)
        quality = int(quality)
    except (ValueError, AttributeError):
        width = 400
        quality = 85
    
    try:
        img = Image.open(image_field.path)
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
        
        # Türkçe debug print
        dosya_boyutu_kb = len(output.getvalue()) / 1024
        print(f"✓ Resim: {image_field.name} | İstenen: {width}x{quality} | Orijinal: {orijinal_boyut} | Sonuç: {dosya_boyutu_kb:.2f}KB")
        
        b64 = base64.b64encode(output.getvalue()).decode()
        return f'data:image/webp;base64,{b64}'
    except Exception as e:
        print(f"✗ Resim optimize hatası: {image_field.name} | {e}")
        return ''