from django.urls import path, re_path
from django_routines.images.views import resim_optimize_et

uygulama_adi = 'django_routines'

url_desenleri = [
    re_path(r'^optimize/(?P<resim_yolu>.+)/(?P<genislik>\d+)/(?P<kalite>\d+)/$', resim_optimize_et, name='resim_optimize_et'),
]

urlpatterns = url_desenleri