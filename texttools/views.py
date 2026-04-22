from django.shortcuts import render
import base64
import random
import string


def texttools_home(request):
    return render(request, 'texttools/home.html')


def word_counter(request):
    result = None
    text = ''
    if request.method == 'POST':
        text = request.POST.get('text', '')
        words = len(text.split()) if text.strip() else 0
        chars = len(text)
        chars_no_space = len(text.replace(' ', ''))
        sentences = text.count('.') + text.count('!') + text.count('?')
        paragraphs = len([p for p in text.split('\n') if p.strip()])
        result = {
            'words': words,
            'chars': chars,
            'chars_no_space': chars_no_space,
            'sentences': sentences,
            'paragraphs': paragraphs,
            'reading_time': max(1, round(words / 200)),
        }
    return render(request, 'texttools/word_counter.html', {'result': result, 'text': text})


def password_generator(request):
    password = None
    length = 16
    if request.method == 'POST':
        length = int(request.POST.get('length', 16))
        use_upper = request.POST.get('upper', 'on') == 'on'
        use_lower = request.POST.get('lower', 'on') == 'on'
        use_digits = request.POST.get('digits', 'on') == 'on'
        use_symbols = request.POST.get('symbols', '') == 'on'
        pool = ''
        if use_upper: pool += string.ascii_uppercase
        if use_lower: pool += string.ascii_lowercase
        if use_digits: pool += string.digits
        if use_symbols: pool += '!@#$%^&*()_+-=[]{}|;:,.<>?'
        if not pool:
            pool = string.ascii_letters + string.digits
        password = ''.join(random.choices(pool, k=length))
    return render(request, 'texttools/password_generator.html', {'password': password, 'length': length})


def text_case_converter(request):
    result = None
    text = ''
    mode = 'upper'
    if request.method == 'POST':
        text = request.POST.get('text', '')
        mode = request.POST.get('mode', 'upper')
        if mode == 'upper':
            result = text.upper()
        elif mode == 'lower':
            result = text.lower()
        elif mode == 'title':
            result = text.title()
        elif mode == 'sentence':
            result = '. '.join(s.strip().capitalize() for s in text.split('.'))
        elif mode == 'alternate':
            result = ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text))
        elif mode == 'reverse':
            result = text[::-1]
    return render(request, 'texttools/text_case.html', {'result': result, 'text': text, 'mode': mode})


def lorem_ipsum(request):
    result = None
    if request.method == 'POST':
        count = int(request.POST.get('count', 3))
        unit = request.POST.get('unit', 'paragraphs')
        base = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        sentences = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.",
            "Duis aute irure dolor in reprehenderit in voluptate velit esse.",
            "Excepteur sint occaecat cupidatat non proident deserunt mollit.",
            "Curabitur pretium tincidunt lacus, nulla facilisis nisl.",
            "Nunc molestie augue vel facilisis varius.",
            "Pellentesque habitant morbi tristique senectus et netus.",
            "Vestibulum ante ipsum primis in faucibus orci luctus.",
            "Fusce dapibus tellus ac cursus commodo, tortor mauris condimentum.",
        ]
        if unit == 'paragraphs':
            result = '\n\n'.join(base for _ in range(count))
        elif unit == 'sentences':
            result = ' '.join((sentences * 10)[:count])
        elif unit == 'words':
            words = (base.split() * 10)[:count]
            result = ' '.join(words)
    return render(request, 'texttools/lorem_ipsum.html', {'result': result})


def base64_tool(request):
    result = None
    mode = 'encode'
    text = ''
    if request.method == 'POST':
        text = request.POST.get('text', '')
        mode = request.POST.get('mode', 'encode')
        try:
            if mode == 'encode':
                result = base64.b64encode(text.encode()).decode()
            else:
                result = base64.b64decode(text.encode()).decode()
        except Exception:
            result = 'Invalid input for decoding.'
    return render(request, 'texttools/base64.html', {'result': result, 'text': text, 'mode': mode})
