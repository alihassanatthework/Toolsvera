from django.urls import path
from . import views

app_name = 'imagetools'

urlpatterns = [
    path('convert/', views.image_convert, name='convert'),
    path('resize/', views.image_resize, name='resize'),
]