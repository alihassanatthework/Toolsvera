from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def calculator_home(request):
    return render(request, 'calculators/home.html')


def bmi_calculator(request):
    result = None
    category = None
    if request.method == 'POST':
        weight = float(request.POST['weight'])
        height = float(request.POST['height']) / 100
        result = round(weight / (height ** 2), 2)
        if result < 18.5:
            category = 'Underweight'
        elif result < 25:
            category = 'Normal weight'
        elif result < 30:
            category = 'Overweight'
        else:
            category = 'Obese'
    return render(request, 'calculators/bmi.html', {'result': result, 'category': category})


def percentage_calculator(request):
    result = None
    if request.method == 'POST':
        value = float(request.POST['value'])
        total = float(request.POST['total'])
        result = round((value / total) * 100, 2)
    return render(request, 'calculators/percentage.html', {'result': result})


def mortgage_calculator(request):
    result = None
    if request.method == 'POST':
        principal = float(request.POST['principal'])
        rate = float(request.POST['rate']) / 100 / 12
        months = int(request.POST['years']) * 12
        if rate > 0:
            payment = principal * rate / (1 - (1 + rate) ** -months)
        else:
            payment = principal / months
        result = round(payment, 2)
    return render(request, 'calculators/mortgage.html', {'result': result})