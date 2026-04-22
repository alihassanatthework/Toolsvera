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
]
