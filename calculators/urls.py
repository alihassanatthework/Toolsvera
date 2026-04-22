from django.urls import path
from . import views

app_name = 'calculators'

urlpatterns = [
    path('', views.home, name='home'),
    path('calculators/', views.calculator_home, name='calculator_home'),
    path('calculators/bmi-calculator/', views.bmi_calculator, name='bmi'),
    path('calculators/percentage-calculator/', views.percentage_calculator, name='percentage'),
    path('calculators/mortgage-calculator/', views.mortgage_calculator, name='mortgage'),
    path('calculators/age-calculator/', views.age_calculator, name='age'),
    path('calculators/date-calculator/', views.date_calculator, name='date'),
    path('calculators/tip-calculator/', views.tip_calculator, name='tip'),
    path('calculators/tax-calculator/', views.tax_calculator, name='tax'),
    path('calculators/loan-calculator/', views.loan_calculator, name='loan'),
    path('calculators/compound-interest-calculator/', views.compound_interest, name='compound_interest'),
    path('calculators/unit-converter/', views.unit_converter, name='unit_converter'),
    path('calculators/gpa-calculator/', views.gpa_calculator, name='gpa'),
    path('calculators/grade-calculator/', views.grade_calculator, name='grade'),
    path('calculators/scientific-calculator/', views.scientific_calculator, name='scientific'),
    path('calculators/fraction-calculator/', views.fraction_calculator, name='fraction'),
    path('calculators/speed-calculator/', views.speed_calculator, name='speed'),
    path('calculators/area-calculator/', views.area_calculator, name='area'),
    path('calculators/calorie-calculator/', views.calorie_calculator, name='calorie'),
    path('calculators/body-fat-calculator/', views.body_fat_calculator, name='body_fat'),
    path('calculators/fuel-cost-calculator/', views.fuel_cost_calculator, name='fuel_cost'),
    path('calculators/discount-calculator/', views.discount_calculator, name='discount'),
    path('calculators/pregnancy-calculator/', views.pregnancy_calculator, name='pregnancy'),
    path('calculators/random-number-generator/', views.random_number, name='random_number'),
    path('calculators/pace-calculator/', views.pace_calculator, name='pace'),
    path('calculators/retirement-calculator/', views.retirement_calculator, name='retirement'),
    path('calculators/average-calculator/', views.average_calculator, name='average'),
    path('calculators/sleep-calculator/', views.sleep_calculator, name='sleep'),
    path('calculators/water-intake-calculator/', views.water_intake_calculator, name='water_intake'),
    path('calculators/percentage-change-calculator/', views.percentage_change_calculator, name='percentage_change'),
]
