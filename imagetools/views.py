from django.shortcuts import render
from django.http import FileResponse
from PIL import Image
from io import BytesIO


def image_convert(request):
    if request.method == 'POST':
        img_file = request.FILES['image']
        fmt = request.POST['format'].upper()
        img = Image.open(img_file).convert('RGB')
        output = BytesIO()
        img.save(output, format=fmt)
        output.seek(0)
        ext = request.POST['format'].lower()
        return FileResponse(output, as_attachment=True, filename=f'converted.{ext}')
    return render(request, 'imagetools/convert.html')


def image_resize(request):
    if request.method == 'POST':
        img_file = request.FILES['image']
        width = int(request.POST['width'])
        height = int(request.POST['height'])
        img = Image.open(img_file)
        img = img.resize((width, height))
        output = BytesIO()
        img.save(output, format='PNG')
        output.seek(0)
        return FileResponse(output, as_attachment=True, filename='resized.png')
    return render(request, 'imagetools/resize.html')