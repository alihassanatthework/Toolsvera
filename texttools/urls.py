from django.urls import path
from . import views

app_name = 'texttools'

urlpatterns = [
    path('', views.texttools_home, name='home'),
    path('word-counter/', views.word_counter, name='word_counter'),
    path('password-generator/', views.password_generator, name='password_generator'),
    path('text-case-converter/', views.text_case_converter, name='text_case'),
    path('lorem-ipsum-generator/', views.lorem_ipsum, name='lorem_ipsum'),
    path('base64-encoder-decoder/', views.base64_tool, name='base64'),
    path('json-formatter/', views.json_formatter, name='json_formatter'),
    path('url-encoder-decoder/', views.url_encoder, name='url_encoder'),
    path('remove-duplicate-lines/', views.remove_duplicates, name='remove_duplicates'),
    path('qr-code-generator/', views.qr_generator, name='qr_generator'),
    path('barcode-generator/', views.barcode_generator, name='barcode_generator'),
]
