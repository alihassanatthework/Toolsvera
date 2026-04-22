from django.shortcuts import render
from django.http import FileResponse
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
import uuid
from django.conf import settings


def _tmp():
    tmp = os.path.join(settings.MEDIA_ROOT, 'tmp')
    os.makedirs(tmp, exist_ok=True)
    return tmp


def image_convert(request):
    if request.method == 'POST':
        try:
            img_file = request.FILES['image']
            fmt = request.POST['format'].upper()
            if fmt == 'JPG':
                fmt = 'JPEG'
            img = Image.open(img_file)
            if fmt == 'JPEG' and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            output = BytesIO()
            img.save(output, format=fmt)
            output.seek(0)
            ext = 'jpg' if fmt == 'JPEG' else request.POST['format'].lower()
            return FileResponse(output, as_attachment=True, filename=f'converted.{ext}')
        except Exception as e:
            return render(request, 'imagetools/convert.html', {'error': str(e)})
    return render(request, 'imagetools/convert.html')


def image_resize(request):
    if request.method == 'POST':
        try:
            img_file = request.FILES['image']
            img = Image.open(img_file)
            fmt = img.format or 'PNG'
            if request.POST.get('keep_ratio'):
                width = int(request.POST['width'])
                ratio = width / img.width
                height = int(img.height * ratio)
            else:
                width = int(request.POST['width'])
                height = int(request.POST['height'])
            img = img.resize((width, height), Image.LANCZOS)
            output = BytesIO()
            save_fmt = 'JPEG' if fmt == 'JPEG' else 'PNG'
            img.save(output, format=save_fmt)
            output.seek(0)
            ext = 'jpg' if save_fmt == 'JPEG' else 'png'
            return FileResponse(output, as_attachment=True, filename=f'resized.{ext}')
        except Exception as e:
            return render(request, 'imagetools/resize.html', {'error': str(e)})
    return render(request, 'imagetools/resize.html')


def image_compress(request):
    if request.method == 'POST':
        try:
            img_file = request.FILES['image']
            quality = int(request.POST.get('quality', 70))
            img = Image.open(img_file).convert('RGB')
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            return FileResponse(output, as_attachment=True, filename='compressed.jpg')
        except Exception as e:
            return render(request, 'imagetools/compress.html', {'error': str(e)})
    return render(request, 'imagetools/compress.html')


def image_rotate(request):
    if request.method == 'POST':
        try:
            img_file = request.FILES['image']
            action = request.POST.get('action', 'rotate_90')
            img = Image.open(img_file)
            fmt = img.format or 'PNG'
            if action == 'rotate_90':
                img = img.rotate(90, expand=True)
            elif action == 'rotate_180':
                img = img.rotate(180, expand=True)
            elif action == 'rotate_270':
                img = img.rotate(270, expand=True)
            elif action == 'flip_h':
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif action == 'flip_v':
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
            output = BytesIO()
            save_fmt = 'JPEG' if fmt == 'JPEG' else 'PNG'
            if save_fmt == 'JPEG' and img.mode == 'RGBA':
                img = img.convert('RGB')
            img.save(output, format=save_fmt)
            output.seek(0)
            ext = 'jpg' if save_fmt == 'JPEG' else 'png'
            return FileResponse(output, as_attachment=True, filename=f'rotated.{ext}')
        except Exception as e:
            return render(request, 'imagetools/rotate.html', {'error': str(e)})
    return render(request, 'imagetools/rotate.html')


def image_crop(request):
    if request.method == 'POST':
        try:
            img_file = request.FILES['image']
            img = Image.open(img_file)
            fmt = img.format or 'PNG'
            x = int(request.POST['x'])
            y = int(request.POST['y'])
            w = int(request.POST['width'])
            h = int(request.POST['height'])
            img = img.crop((x, y, x + w, y + h))
            output = BytesIO()
            save_fmt = 'JPEG' if fmt == 'JPEG' else 'PNG'
            if save_fmt == 'JPEG' and img.mode == 'RGBA':
                img = img.convert('RGB')
            img.save(output, format=save_fmt)
            output.seek(0)
            ext = 'jpg' if save_fmt == 'JPEG' else 'png'
            return FileResponse(output, as_attachment=True, filename=f'cropped.{ext}')
        except Exception as e:
            return render(request, 'imagetools/crop.html', {'error': str(e)})
    return render(request, 'imagetools/crop.html')


def image_to_pdf(request):
    if request.method == 'POST':
        try:
            files = request.FILES.getlist('images')
            images = [Image.open(f).convert('RGB') for f in files]
            uid = str(uuid.uuid4())
            output_path = os.path.join(_tmp(), f'{uid}_images.pdf')
            if images:
                images[0].save(output_path, save_all=True, append_images=images[1:])
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename='images.pdf')
        except Exception as e:
            return render(request, 'imagetools/to_pdf.html', {'error': str(e)})
    return render(request, 'imagetools/to_pdf.html')


def image_watermark(request):
    if request.method == 'POST':
        try:
            img_file = request.FILES['image']
            text = request.POST.get('text', 'ToolsVera')
            opacity = int(request.POST.get('opacity', 128))
            img = Image.open(img_file).convert('RGBA')
            overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)
            font_size = max(img.width // 10, 20)
            try:
                font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', font_size)
            except Exception:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            x = (img.width - tw) // 2
            y = (img.height - th) // 2
            draw.text((x, y), text, font=font, fill=(128, 128, 128, opacity))
            watermarked = Image.alpha_composite(img, overlay).convert('RGB')
            output = BytesIO()
            watermarked.save(output, format='JPEG', quality=95)
            output.seek(0)
            return FileResponse(output, as_attachment=True, filename='watermarked.jpg')
        except Exception as e:
            return render(request, 'imagetools/watermark.html', {'error': str(e)})
    return render(request, 'imagetools/watermark.html')
