from django.urls import path
from . import views

app_name = 'texttools'

urlpatterns = [
    path('', views.texttools_home, name='home'),
    path('word-counter/', views.word_counter, name='word_counter'),
    path('password-generator/', views.password_generator, name='password_generator'),
    path('text-case/', views.text_case_converter, name='text_case'),
    path('lorem-ipsum/', views.lorem_ipsum, name='lorem_ipsum'),
    path('base64/', views.base64_tool, name='base64'),
    path('json-formatter/', views.json_formatter, name='json_formatter'),
    path('url-encoder/', views.url_encoder, name='url_encoder'),
    path('remove-duplicates/', views.remove_duplicates, name='remove_duplicates'),
]
