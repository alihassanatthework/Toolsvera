from django.urls import path
from . import views

app_name = 'filetools'

urlpatterns = [
    path('word-to-pdf/', views.word_to_pdf, name='word_to_pdf'),
]