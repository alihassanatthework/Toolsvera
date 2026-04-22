from django.urls import path
from . import views

app_name = 'imagetools'

urlpatterns = [
    path('convert/', views.image_convert, name='convert'),
    path('resize/', views.image_resize, name='resize'),
    path('compress/', views.image_compress, name='compress'),
    path('rotate/', views.image_rotate, name='rotate'),
    path('crop/', views.image_crop, name='crop'),
    path('to-pdf/', views.image_to_pdf, name='to_pdf'),
    path('watermark/', views.image_watermark, name='watermark'),
]
