from django.urls import path, re_path
from django_routines.images.views import resim_optimize_et

app_name = 'django_routines'

url_desenleri = [
    re_path(r'^optimize/genislik=(?P<genislik>\d+|orig)/kalite=(?P<kalite>\d+)/(?P<resim_yolu>.+)$', resim_optimize_et, name='resim_optimize_et'),
]

urlpatterns = url_desenleri