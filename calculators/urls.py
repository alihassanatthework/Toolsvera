from django.urls import path
from . import views

app_name = 'calculators'

urlpatterns = [
    path('', views.home, name='home'),
    path('calculators/', views.calculator_home, name='calculator_home'),
    path('calculators/bmi/', views.bmi_calculator, name='bmi'),
    path('calculators/percentage/', views.percentage_calculator, name='percentage'),
    path('calculators/mortgage/', views.mortgage_calculator, name='mortgage'),
]