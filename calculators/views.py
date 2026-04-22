from django.shortcuts import render
from datetime import date, datetime
from math import gcd


def home(request):
    return render(request, 'home.html')


def calculator_home(request):
    return render(request, 'calculators/home.html')


def bmi_calculator(request):
    result = None
    category = None
    if request.method == 'POST':
        try:
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
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/bmi.html', {'result': result, 'category': category})


def percentage_calculator(request):
    result = None
    if request.method == 'POST':
        try:
            value = float(request.POST['value'])
            total = float(request.POST['total'])
            result = round((value / total) * 100, 2)
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/percentage.html', {'result': result})


def mortgage_calculator(request):
    result = None
    total_payment = None
    total_interest = None
    if request.method == 'POST':
        try:
            principal = float(request.POST['principal'])
            rate = float(request.POST['rate']) / 100 / 12
            months = int(request.POST['years']) * 12
            if rate > 0:
                payment = principal * rate / (1 - (1 + rate) ** -months)
            else:
                payment = principal / months
            result = round(payment, 2)
            total_payment = round(payment * months, 2)
            total_interest = round(total_payment - principal, 2)
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/mortgage.html', {
        'result': result,
        'total_payment': total_payment,
        'total_interest': total_interest,
    })


def age_calculator(request):
    result = None
    if request.method == 'POST':
        try:
            dob = datetime.strptime(request.POST['dob'], '%Y-%m-%d').date()
            today = date.today()
            years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            months = (today.month - dob.month) % 12
            days = (today - dob.replace(year=today.year)).days % 30
            total_days = (today - dob).days
            result = {'years': years, 'months': months, 'days': days, 'total_days': total_days}
        except (ValueError, TypeError):
            pass
    return render(request, 'calculators/age.html', {'result': result})


def date_calculator(request):
    result = None
    if request.method == 'POST':
        try:
            d1 = datetime.strptime(request.POST['date1'], '%Y-%m-%d').date()
            d2 = datetime.strptime(request.POST['date2'], '%Y-%m-%d').date()
            delta = abs((d2 - d1).days)
            weeks = delta // 7
            remaining_days = delta % 7
            result = {'days': delta, 'weeks': weeks, 'remaining_days': remaining_days}
        except (ValueError, TypeError):
            pass
    return render(request, 'calculators/date.html', {'result': result})


def tip_calculator(request):
    result = None
    if request.method == 'POST':
        try:
            bill = float(request.POST['bill'])
            tip_pct = float(request.POST['tip'])
            people = int(request.POST.get('people', 1)) or 1
            tip_amount = round(bill * tip_pct / 100, 2)
            total = round(bill + tip_amount, 2)
            per_person = round(total / people, 2)
            result = {'tip': tip_amount, 'total': total, 'per_person': per_person, 'people': people}
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/tip.html', {'result': result})


def tax_calculator(request):
    result = None
    if request.method == 'POST':
        try:
            income = float(request.POST['income'])
            tax_rate = float(request.POST['tax_rate'])
            tax = round(income * tax_rate / 100, 2)
            after_tax = round(income - tax, 2)
            result = {'tax': tax, 'after_tax': after_tax, 'income': income}
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/tax.html', {'result': result})


def loan_calculator(request):
    result = None
    if request.method == 'POST':
        try:
            principal = float(request.POST['principal'])
            rate = float(request.POST['rate']) / 100 / 12
            months = int(request.POST['months'])
            if rate > 0:
                payment = principal * rate / (1 - (1 + rate) ** -months)
            else:
                payment = principal / months
            total = round(payment * months, 2)
            interest = round(total - principal, 2)
            result = {'payment': round(payment, 2), 'total': total, 'interest': interest}
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/loan.html', {'result': result})


def compound_interest(request):
    result = None
    if request.method == 'POST':
        try:
            principal = float(request.POST['principal'])
            rate = float(request.POST['rate']) / 100
            n = int(request.POST['compound'])
            years = float(request.POST['years'])
            amount = principal * (1 + rate / n) ** (n * years)
            interest = round(amount - principal, 2)
            result = {'amount': round(amount, 2), 'interest': interest, 'principal': principal}
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/compound_interest.html', {'result': result})


def unit_converter(request):
    result = None
    category = request.POST.get('category', 'length') if request.method == 'POST' else 'length'
    value = request.POST.get('value', '')
    from_unit = request.POST.get('from_unit', '')
    to_unit = request.POST.get('to_unit', '')

    conversions = {
        'length': {
            'meter': 1, 'kilometer': 1000, 'centimeter': 0.01, 'millimeter': 0.001,
            'mile': 1609.344, 'yard': 0.9144, 'foot': 0.3048, 'inch': 0.0254,
        },
        'weight': {
            'kilogram': 1, 'gram': 0.001, 'milligram': 0.000001,
            'pound': 0.453592, 'ounce': 0.0283495, 'ton': 1000,
        },
        'temperature': {},
        'area': {
            'sq_meter': 1, 'sq_kilometer': 1000000, 'sq_foot': 0.092903,
            'sq_inch': 0.00064516, 'acre': 4046.86, 'hectare': 10000,
        },
        'speed': {
            'mps': 1, 'kph': 0.277778, 'mph': 0.44704, 'knot': 0.514444,
        },
    }

    if request.method == 'POST' and value:
        try:
            val = float(value)
            if category == 'temperature':
                if from_unit == 'celsius' and to_unit == 'fahrenheit':
                    result = round(val * 9/5 + 32, 4)
                elif from_unit == 'fahrenheit' and to_unit == 'celsius':
                    result = round((val - 32) * 5/9, 4)
                elif from_unit == 'celsius' and to_unit == 'kelvin':
                    result = round(val + 273.15, 4)
                elif from_unit == 'kelvin' and to_unit == 'celsius':
                    result = round(val - 273.15, 4)
                elif from_unit == 'fahrenheit' and to_unit == 'kelvin':
                    result = round((val - 32) * 5/9 + 273.15, 4)
                elif from_unit == 'kelvin' and to_unit == 'fahrenheit':
                    result = round((val - 273.15) * 9/5 + 32, 4)
                else:
                    result = val
            elif category in conversions:
                base = val * conversions[category][from_unit]
                result = round(base / conversions[category][to_unit], 6)
        except (ValueError, KeyError, ZeroDivisionError):
            pass

    return render(request, 'calculators/unit_converter.html', {
        'result': result, 'category': category,
        'value': value, 'from_unit': from_unit, 'to_unit': to_unit,
    })


def gpa_calculator(request):
    result = None
    courses = []
    if request.method == 'POST':
        try:
            grades = request.POST.getlist('grade')
            credits = request.POST.getlist('credits')
            grade_map = {'A+': 4.0, 'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
                         'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'F': 0.0}
            total_points = 0
            total_credits = 0
            for g, c in zip(grades, credits):
                if g and c:
                    pts = grade_map.get(g, 0)
                    cr = float(c)
                    total_points += pts * cr
                    total_credits += cr
                    courses.append({'grade': g, 'credits': cr, 'points': pts})
            if total_credits > 0:
                result = round(total_points / total_credits, 2)
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/gpa.html', {'result': result, 'courses': courses})


def grade_calculator(request):
    result = None
    letter = None
    if request.method == 'POST':
        try:
            scores = request.POST.getlist('score')
            weights = request.POST.getlist('weight')
            total_weight = 0
            weighted_score = 0
            for s, w in zip(scores, weights):
                if s and w:
                    weighted_score += float(s) * float(w) / 100
                    total_weight += float(w)
            if total_weight > 0:
                result = round(weighted_score * 100 / total_weight, 2)
                if result >= 90: letter = 'A'
                elif result >= 80: letter = 'B'
                elif result >= 70: letter = 'C'
                elif result >= 60: letter = 'D'
                else: letter = 'F'
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/grade.html', {'result': result, 'letter': letter})


def scientific_calculator(request):
    return render(request, 'calculators/scientific.html')


def fraction_calculator(request):
    result = None
    result_str = None
    if request.method == 'POST':
        try:
            n1, d1 = int(request.POST['n1']), int(request.POST['d1'])
            n2, d2 = int(request.POST['n2']), int(request.POST['d2'])
            op = request.POST['operation']
            if op == 'add':
                rn, rd = n1 * d2 + n2 * d1, d1 * d2
            elif op == 'subtract':
                rn, rd = n1 * d2 - n2 * d1, d1 * d2
            elif op == 'multiply':
                rn, rd = n1 * n2, d1 * d2
            elif op == 'divide':
                rn, rd = n1 * d2, d1 * n2
            g = gcd(abs(rn), abs(rd))
            rn, rd = rn // g, rd // g
            if rd < 0:
                rn, rd = -rn, -rd
            result = rn / rd
            result_str = f"{rn}/{rd}" if rd != 1 else str(rn)
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/fraction.html', {'result': result, 'result_str': result_str})


def speed_calculator(request):
    result = None
    if request.method == 'POST':
        try:
            calc_for = request.POST['calc_for']
            if calc_for == 'speed':
                dist = float(request.POST['distance'])
                time = float(request.POST['time'])
                result = {'value': round(dist / time, 4), 'label': 'Speed', 'unit': request.POST.get('speed_unit', 'km/h')}
            elif calc_for == 'distance':
                speed = float(request.POST['speed'])
                time = float(request.POST['time'])
                result = {'value': round(speed * time, 4), 'label': 'Distance', 'unit': 'km'}
            elif calc_for == 'time':
                dist = float(request.POST['distance'])
                speed = float(request.POST['speed'])
                result = {'value': round(dist / speed, 4), 'label': 'Time', 'unit': 'hours'}
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/speed.html', {'result': result})


def area_calculator(request):
    result = None
    shape = request.POST.get('shape', 'rectangle') if request.method == 'POST' else 'rectangle'
    if request.method == 'POST':
        try:
            import math
            if shape == 'rectangle':
                result = round(float(request.POST['length']) * float(request.POST['width']), 4)
            elif shape == 'circle':
                result = round(math.pi * float(request.POST['radius']) ** 2, 4)
            elif shape == 'triangle':
                result = round(0.5 * float(request.POST['base']) * float(request.POST['height']), 4)
            elif shape == 'square':
                result = round(float(request.POST['side']) ** 2, 4)
            elif shape == 'trapezoid':
                result = round(0.5 * (float(request.POST['a']) + float(request.POST['b'])) * float(request.POST['height']), 4)
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/area.html', {'result': result, 'shape': shape})


def calorie_calculator(request):
    result = None
    if request.method == 'POST':
        try:
            weight = float(request.POST['weight'])
            height = float(request.POST['height'])
            age = int(request.POST['age'])
            gender = request.POST['gender']
            activity = float(request.POST['activity'])
            if gender == 'male':
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else:
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
            tdee = round(bmr * activity, 0)
            result = {
                'bmr': round(bmr, 0),
                'tdee': tdee,
                'lose': tdee - 500,
                'gain': tdee + 500,
            }
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/calorie.html', {'result': result})


def body_fat_calculator(request):
    result = None
    if request.method == 'POST':
        try:
            import math
            gender = request.POST['gender']
            height = float(request.POST['height'])
            waist = float(request.POST['waist'])
            neck = float(request.POST['neck'])
            if gender == 'male':
                bf = 495 / (1.0324 - 0.19077 * math.log10(waist - neck) + 0.15456 * math.log10(height)) - 450
            else:
                hip = float(request.POST['hip'])
                bf = 495 / (1.29579 - 0.35004 * math.log10(waist + hip - neck) + 0.22100 * math.log10(height)) - 450
            bf = round(bf, 1)
            if gender == 'male':
                category = 'Essential' if bf < 6 else 'Athlete' if bf < 14 else 'Fitness' if bf < 18 else 'Average' if bf < 25 else 'Obese'
            else:
                category = 'Essential' if bf < 14 else 'Athlete' if bf < 21 else 'Fitness' if bf < 25 else 'Average' if bf < 32 else 'Obese'
            result = {'bf': bf, 'category': category}
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/body_fat.html', {'result': result})


def fuel_cost_calculator(request):
    result = None
    if request.method == 'POST':
        try:
            distance = float(request.POST['distance'])
            efficiency = float(request.POST['efficiency'])
            price = float(request.POST['price'])
            fuel_used = distance / efficiency
            total_cost = round(fuel_used * price, 2)
            result = {'fuel': round(fuel_used, 2), 'cost': total_cost}
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/fuel_cost.html', {'result': result})


def discount_calculator(request):
    result = None
    if request.method == 'POST':
        try:
            price = float(request.POST['price'])
            discount = float(request.POST['discount'])
            saved = round(price * discount / 100, 2)
            final = round(price - saved, 2)
            result = {'saved': saved, 'final': final, 'original': price}
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/discount.html', {'result': result})


def pregnancy_calculator(request):
    result = None
    if request.method == 'POST':
        try:
            lmp = datetime.strptime(request.POST['lmp'], '%Y-%m-%d').date()
            from datetime import timedelta
            due_date = lmp + timedelta(days=280)
            today = date.today()
            days_pregnant = (today - lmp).days
            weeks = days_pregnant // 7
            days_rem = days_pregnant % 7
            trimester = 1 if weeks < 13 else 2 if weeks < 27 else 3
            days_left = (due_date - today).days
            result = {
                'due_date': due_date.strftime('%B %d, %Y'),
                'weeks': weeks,
                'days': days_rem,
                'trimester': trimester,
                'days_left': max(0, days_left),
            }
        except (ValueError, TypeError):
            pass
    return render(request, 'calculators/pregnancy.html', {'result': result})


def random_number(request):
    result = None
    if request.method == 'POST':
        try:
            import random
            min_val = int(request.POST['min'])
            max_val = int(request.POST['max'])
            count = min(int(request.POST.get('count', 1)), 20)
            result = [random.randint(min_val, max_val) for _ in range(count)]
        except (ValueError, TypeError):
            pass
    return render(request, 'calculators/random_number.html', {'result': result})


def pace_calculator(request):
    result = None
    if request.method == 'POST':
        try:
            calc_for = request.POST['calc_for']
            if calc_for == 'pace':
                hours = int(request.POST.get('hours', 0))
                minutes = int(request.POST['minutes'])
                seconds = int(request.POST.get('seconds', 0))
                distance = float(request.POST['distance'])
                total_secs = hours * 3600 + minutes * 60 + seconds
                pace_secs = total_secs / distance
                pm = int(pace_secs // 60)
                ps = int(pace_secs % 60)
                result = {'label': 'Pace', 'value': f"{pm}:{ps:02d}", 'unit': 'min/km'}
            elif calc_for == 'time':
                pace_min = int(request.POST['pace_min'])
                pace_sec = int(request.POST.get('pace_sec', 0))
                distance = float(request.POST['distance'])
                total = (pace_min * 60 + pace_sec) * distance
                h = int(total // 3600)
                m = int((total % 3600) // 60)
                s = int(total % 60)
                result = {'label': 'Finish Time', 'value': f"{h}:{m:02d}:{s:02d}", 'unit': ''}
            elif calc_for == 'distance':
                hours = int(request.POST.get('hours', 0))
                minutes = int(request.POST['minutes'])
                seconds = int(request.POST.get('seconds', 0))
                pace_min = int(request.POST['pace_min'])
                pace_sec = int(request.POST.get('pace_sec', 0))
                total_secs = hours * 3600 + minutes * 60 + seconds
                pace_secs = pace_min * 60 + pace_sec
                dist = round(total_secs / pace_secs, 2)
                result = {'label': 'Distance', 'value': dist, 'unit': 'km'}
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/pace.html', {'result': result})


def retirement_calculator(request):
    result = None
    if request.method == 'POST':
        try:
            current_age = int(request.POST['current_age'])
            retirement_age = int(request.POST['retirement_age'])
            savings = float(request.POST['savings'])
            monthly = float(request.POST['monthly'])
            rate = float(request.POST['rate']) / 100 / 12
            years = retirement_age - current_age
            months = years * 12
            if rate > 0:
                future = savings * (1 + rate) ** months + monthly * (((1 + rate) ** months - 1) / rate)
            else:
                future = savings + monthly * months
            result = {
                'future': round(future, 2),
                'years': years,
                'contributed': round(monthly * months, 2),
            }
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'calculators/retirement.html', {'result': result})
