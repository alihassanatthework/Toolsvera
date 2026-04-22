from django.urls import path
from . import views

app_name = 'calculators'

urlpatterns = [
    path('', views.home, name='home'),
    path('calculators/', views.calculator_home, name='calculator_home'),
    path('calculators/bmi/', views.bmi_calculator, name='bmi'),
    path('calculators/percentage/', views.percentage_calculator, name='percentage'),
    path('calculators/mortgage/', views.mortgage_calculator, name='mortgage'),
    path('calculators/age/', views.age_calculator, name='age'),
    path('calculators/date/', views.date_calculator, name='date'),
    path('calculators/tip/', views.tip_calculator, name='tip'),
    path('calculators/tax/', views.tax_calculator, name='tax'),
    path('calculators/loan/', views.loan_calculator, name='loan'),
    path('calculators/compound-interest/', views.compound_interest, name='compound_interest'),
    path('calculators/unit-converter/', views.unit_converter, name='unit_converter'),
    path('calculators/gpa/', views.gpa_calculator, name='gpa'),
    path('calculators/grade/', views.grade_calculator, name='grade'),
    path('calculators/scientific/', views.scientific_calculator, name='scientific'),
    path('calculators/fraction/', views.fraction_calculator, name='fraction'),
    path('calculators/speed/', views.speed_calculator, name='speed'),
    path('calculators/area/', views.area_calculator, name='area'),
    path('calculators/calorie/', views.calorie_calculator, name='calorie'),
    path('calculators/body-fat/', views.body_fat_calculator, name='body_fat'),
    path('calculators/fuel-cost/', views.fuel_cost_calculator, name='fuel_cost'),
    path('calculators/discount/', views.discount_calculator, name='discount'),
    path('calculators/pregnancy/', views.pregnancy_calculator, name='pregnancy'),
    path('calculators/random-number/', views.random_number, name='random_number'),
    path('calculators/pace/', views.pace_calculator, name='pace'),
    path('calculators/retirement/', views.retirement_calculator, name='retirement'),
    path('calculators/average/', views.average_calculator, name='average'),
    path('calculators/sleep/', views.sleep_calculator, name='sleep'),
    path('calculators/water-intake/', views.water_intake_calculator, name='water_intake'),
    path('calculators/percentage-change/', views.percentage_change_calculator, name='percentage_change'),
]
