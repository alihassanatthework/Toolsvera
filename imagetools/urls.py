from django.urls import path
from . import views

app_name = 'imagetools'

urlpatterns = [
    path('image-converter/', views.image_convert, name='convert'),
    path('resize-image/', views.image_resize, name='resize'),
    path('compress-image/', views.image_compress, name='compress'),
    path('rotate-image/', views.image_rotate, name='rotate'),
    path('crop-image/', views.image_crop, name='crop'),
    path('image-to-pdf/', views.image_to_pdf, name='to_pdf'),
    path('watermark-image/', views.image_watermark, name='watermark'),
]
