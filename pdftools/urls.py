from django.urls import path
from . import views

app_name = 'pdftools'

urlpatterns = [
    path('merge/', views.pdf_merge, name='merge'),
    path('split/', views.pdf_split, name='split'),
    path('to-word/', views.pdf_to_word, name='to_word'),
    path('compress/', views.pdf_compress, name='compress'),
]