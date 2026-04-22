from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from pypdf import PdfWriter, PdfReader
import uuid
import os
import io
from django.conf import settings


def _tmp():
    tmp = os.path.join(settings.MEDIA_ROOT, 'tmp')
    os.makedirs(tmp, exist_ok=True)
    return tmp


def pdf_merge(request):
    if request.method == 'POST':
        try:
            files = request.FILES.getlist('pdfs')
            writer = PdfWriter()
            for f in files:
                reader = PdfReader(f)
                for page in reader.pages:
                    writer.add_page(page)
            uid = str(uuid.uuid4())
            output_path = os.path.join(_tmp(), f'{uid}_merged.pdf')
            with open(output_path, 'wb') as out:
                writer.write(out)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename='merged.pdf')
        except Exception as e:
            return render(request, 'pdftools/merge.html', {'error': str(e)})
    return render(request, 'pdftools/merge.html')


def pdf_split(request):
    if request.method == 'POST':
        try:
            f = request.FILES['pdf']
            reader = PdfReader(f)
            total = len(reader.pages)
            pages_input = request.POST.get('pages', '').strip()
            uid = str(uuid.uuid4())

            selected = []
            if pages_input:
                for part in pages_input.split(','):
                    part = part.strip()
                    if '-' in part:
                        a, b = part.split('-')
                        selected.extend(range(int(a) - 1, min(int(b), total)))
                    else:
                        idx = int(part) - 1
                        if 0 <= idx < total:
                            selected.append(idx)
            else:
                selected = list(range(total))

            writer = PdfWriter()
            for idx in selected:
                writer.add_page(reader.pages[idx])

            output_path = os.path.join(_tmp(), f'{uid}_split.pdf')
            with open(output_path, 'wb') as out:
                writer.write(out)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename='split.pdf')
        except Exception as e:
            return render(request, 'pdftools/split.html', {'error': str(e)})
    return render(request, 'pdftools/split.html')


def pdf_to_word(request):
    if request.method == 'POST':
        try:
            from pdf2docx import Converter
            f = request.FILES['pdf']
            uid = str(uuid.uuid4())
            pdf_path = os.path.join(_tmp(), f'{uid}.pdf')
            docx_path = os.path.join(_tmp(), f'{uid}.docx')
            with open(pdf_path, 'wb') as out:
                for chunk in f.chunks():
                    out.write(chunk)
            cv = Converter(pdf_path)
            cv.convert(docx_path)
            cv.close()
            return FileResponse(open(docx_path, 'rb'), as_attachment=True, filename='converted.docx')
        except Exception as e:
            return render(request, 'pdftools/to_word.html', {'error': str(e)})
    return render(request, 'pdftools/to_word.html')


def pdf_compress(request):
    if request.method == 'POST':
        try:
            f = request.FILES['pdf']
            reader = PdfReader(f)
            writer = PdfWriter()
            for page in reader.pages:
                page.compress_content_streams()
                writer.add_page(page)
            uid = str(uuid.uuid4())
            output_path = os.path.join(_tmp(), f'{uid}_compressed.pdf')
            with open(output_path, 'wb') as out:
                writer.write(out)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename='compressed.pdf')
        except Exception as e:
            return render(request, 'pdftools/compress.html', {'error': str(e)})
    return render(request, 'pdftools/compress.html')


def pdf_to_jpg(request):
    if request.method == 'POST':
        try:
            import fitz
            import zipfile
            f = request.FILES['pdf']
            uid = str(uuid.uuid4())
            pdf_path = os.path.join(_tmp(), f'{uid}.pdf')
            with open(pdf_path, 'wb') as out:
                for chunk in f.chunks():
                    out.write(chunk)
            doc = fitz.open(pdf_path)
            zip_path = os.path.join(_tmp(), f'{uid}_pages.zip')
            with zipfile.ZipFile(zip_path, 'w') as zf:
                for i, page in enumerate(doc):
                    mat = fitz.Matrix(2, 2)
                    pix = page.get_pixmap(matrix=mat)
                    img_path = os.path.join(_tmp(), f'{uid}_page_{i+1}.jpg')
                    pix.save(img_path)
                    zf.write(img_path, f'page_{i+1}.jpg')
            return FileResponse(open(zip_path, 'rb'), as_attachment=True, filename='pdf_pages.zip')
        except Exception as e:
            return render(request, 'pdftools/to_jpg.html', {'error': str(e)})
    return render(request, 'pdftools/to_jpg.html')


def jpg_to_pdf(request):
    if request.method == 'POST':
        try:
            from PIL import Image
            files = request.FILES.getlist('images')
            images = []
            for f in files:
                img = Image.open(f).convert('RGB')
                images.append(img)
            uid = str(uuid.uuid4())
            output_path = os.path.join(_tmp(), f'{uid}_images.pdf')
            if images:
                images[0].save(output_path, save_all=True, append_images=images[1:])
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename='images.pdf')
        except Exception as e:
            return render(request, 'pdftools/jpg_to_pdf.html', {'error': str(e)})
    return render(request, 'pdftools/jpg_to_pdf.html')


def pdf_rotate(request):
    if request.method == 'POST':
        try:
            f = request.FILES['pdf']
            angle = int(request.POST.get('angle', 90))
            reader = PdfReader(f)
            writer = PdfWriter()
            for page in reader.pages:
                page.rotate(angle)
                writer.add_page(page)
            uid = str(uuid.uuid4())
            output_path = os.path.join(_tmp(), f'{uid}_rotated.pdf')
            with open(output_path, 'wb') as out:
                writer.write(out)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename='rotated.pdf')
        except Exception as e:
            return render(request, 'pdftools/rotate.html', {'error': str(e)})
    return render(request, 'pdftools/rotate.html')


def pdf_remove_pages(request):
    if request.method == 'POST':
        try:
            f = request.FILES['pdf']
            pages_input = request.POST.get('pages', '').strip()
            reader = PdfReader(f)
            total = len(reader.pages)
            remove = set()
            for part in pages_input.split(','):
                part = part.strip()
                if '-' in part:
                    a, b = part.split('-')
                    remove.update(range(int(a) - 1, min(int(b), total)))
                elif part:
                    remove.add(int(part) - 1)
            writer = PdfWriter()
            for i, page in enumerate(reader.pages):
                if i not in remove:
                    writer.add_page(page)
            uid = str(uuid.uuid4())
            output_path = os.path.join(_tmp(), f'{uid}_removed.pdf')
            with open(output_path, 'wb') as out:
                writer.write(out)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename='pages_removed.pdf')
        except Exception as e:
            return render(request, 'pdftools/remove_pages.html', {'error': str(e)})
    return render(request, 'pdftools/remove_pages.html')


def pdf_extract_pages(request):
    if request.method == 'POST':
        try:
            f = request.FILES['pdf']
            pages_input = request.POST.get('pages', '').strip()
            reader = PdfReader(f)
            total = len(reader.pages)
            selected = []
            for part in pages_input.split(','):
                part = part.strip()
                if '-' in part:
                    a, b = part.split('-')
                    selected.extend(range(int(a) - 1, min(int(b), total)))
                elif part:
                    selected.append(int(part) - 1)
            writer = PdfWriter()
            for idx in selected:
                if 0 <= idx < total:
                    writer.add_page(reader.pages[idx])
            uid = str(uuid.uuid4())
            output_path = os.path.join(_tmp(), f'{uid}_extracted.pdf')
            with open(output_path, 'wb') as out:
                writer.write(out)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename='extracted.pdf')
        except Exception as e:
            return render(request, 'pdftools/extract_pages.html', {'error': str(e)})
    return render(request, 'pdftools/extract_pages.html')


def pdf_add_page_numbers(request):
    if request.method == 'POST':
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from pypdf import PdfWriter, PdfReader
            import io

            f = request.FILES['pdf']
            position = request.POST.get('position', 'bottom-center')
            start = int(request.POST.get('start', 1))
            reader = PdfReader(f)
            writer = PdfWriter()

            for i, page in enumerate(reader.pages):
                w = float(page.mediabox.width)
                h = float(page.mediabox.height)
                packet = io.BytesIO()
                c = canvas.Canvas(packet, pagesize=(w, h))
                c.setFont('Helvetica', 10)
                num = str(i + start)
                if 'bottom' in position:
                    y = 20
                else:
                    y = h - 20
                if 'center' in position:
                    x = w / 2
                    c.drawCentredString(x, y, num)
                elif 'left' in position:
                    c.drawString(30, y, num)
                else:
                    c.drawRightString(w - 30, y, num)
                c.save()
                packet.seek(0)
                overlay = PdfReader(packet)
                page.merge_page(overlay.pages[0])
                writer.add_page(page)

            uid = str(uuid.uuid4())
            output_path = os.path.join(_tmp(), f'{uid}_numbered.pdf')
            with open(output_path, 'wb') as out:
                writer.write(out)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename='numbered.pdf')
        except Exception as e:
            return render(request, 'pdftools/add_page_numbers.html', {'error': str(e)})
    return render(request, 'pdftools/add_page_numbers.html')


def pdf_watermark(request):
    if request.method == 'POST':
        try:
            from reportlab.pdfgen import canvas
            import io

            f = request.FILES['pdf']
            text = request.POST.get('text', 'CONFIDENTIAL')
            opacity = float(request.POST.get('opacity', 0.3))
            reader = PdfReader(f)
            writer = PdfWriter()

            for page in reader.pages:
                w = float(page.mediabox.width)
                h = float(page.mediabox.height)
                packet = io.BytesIO()
                c = canvas.Canvas(packet, pagesize=(w, h))
                c.setFont('Helvetica-Bold', 40)
                c.setFillColorRGB(0.5, 0.5, 0.5, alpha=opacity)
                c.saveState()
                c.translate(w / 2, h / 2)
                c.rotate(45)
                c.drawCentredString(0, 0, text)
                c.restoreState()
                c.save()
                packet.seek(0)
                overlay = PdfReader(packet)
                page.merge_page(overlay.pages[0])
                writer.add_page(page)

            uid = str(uuid.uuid4())
            output_path = os.path.join(_tmp(), f'{uid}_watermarked.pdf')
            with open(output_path, 'wb') as out:
                writer.write(out)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename='watermarked.pdf')
        except Exception as e:
            return render(request, 'pdftools/watermark.html', {'error': str(e)})
    return render(request, 'pdftools/watermark.html')


def pdf_protect(request):
    if request.method == 'POST':
        try:
            f = request.FILES['pdf']
            password = request.POST.get('password', '')
            reader = PdfReader(f)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.encrypt(password)
            uid = str(uuid.uuid4())
            output_path = os.path.join(_tmp(), f'{uid}_protected.pdf')
            with open(output_path, 'wb') as out:
                writer.write(out)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename='protected.pdf')
        except Exception as e:
            return render(request, 'pdftools/protect.html', {'error': str(e)})
    return render(request, 'pdftools/protect.html')


def pdf_unlock(request):
    if request.method == 'POST':
        try:
            f = request.FILES['pdf']
            password = request.POST.get('password', '')
            reader = PdfReader(f)
            if reader.is_encrypted:
                reader.decrypt(password)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            uid = str(uuid.uuid4())
            output_path = os.path.join(_tmp(), f'{uid}_unlocked.pdf')
            with open(output_path, 'wb') as out:
                writer.write(out)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename='unlocked.pdf')
        except Exception as e:
            return render(request, 'pdftools/unlock.html', {'error': str(e)})
    return render(request, 'pdftools/unlock.html')


def pdf_organize(request):
    if request.method == 'POST':
        try:
            f = request.FILES['pdf']
            order_input = request.POST.get('order', '').strip()
            reader = PdfReader(f)
            total = len(reader.pages)
            order = [int(x.strip()) - 1 for x in order_input.split(',') if x.strip()]
            writer = PdfWriter()
            for idx in order:
                if 0 <= idx < total:
                    writer.add_page(reader.pages[idx])
            uid = str(uuid.uuid4())
            output_path = os.path.join(_tmp(), f'{uid}_organized.pdf')
            with open(output_path, 'wb') as out:
                writer.write(out)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename='organized.pdf')
        except Exception as e:
            return render(request, 'pdftools/organize.html', {'error': str(e)})
    return render(request, 'pdftools/organize.html')


# Coming Soon stubs
def coming_soon(request, tool_name, tool_desc):
    return render(request, 'coming_soon.html', {'tool_name': tool_name, 'tool_desc': tool_desc})


def pdf_to_powerpoint(request):
    return render(request, 'coming_soon.html', {'tool_name': 'PDF to PowerPoint', 'tool_desc': 'Convert PDF files to editable PowerPoint presentations.'})


def pdf_to_excel(request):
    return render(request, 'coming_soon.html', {'tool_name': 'PDF to Excel', 'tool_desc': 'Extract tables from PDF into editable Excel spreadsheets.'})


def powerpoint_to_pdf(request):
    return render(request, 'coming_soon.html', {'tool_name': 'PowerPoint to PDF', 'tool_desc': 'Convert PowerPoint presentations to PDF format.'})


def excel_to_pdf(request):
    return render(request, 'coming_soon.html', {'tool_name': 'Excel to PDF', 'tool_desc': 'Convert Excel spreadsheets to PDF format.'})


def html_to_pdf(request):
    return render(request, 'coming_soon.html', {'tool_name': 'HTML to PDF', 'tool_desc': 'Convert any web page or HTML file to PDF.'})


def pdf_ocr(request):
    return render(request, 'coming_soon.html', {'tool_name': 'OCR PDF', 'tool_desc': 'Extract text from scanned PDFs using optical character recognition.'})


def pdf_sign(request):
    return render(request, 'coming_soon.html', {'tool_name': 'Sign PDF', 'tool_desc': 'Digitally sign your PDF documents online.'})


def pdf_edit(request):
    return render(request, 'coming_soon.html', {'tool_name': 'Edit PDF', 'tool_desc': 'Add text, images and annotations to your PDF.'})


def pdf_repair(request):
    return render(request, 'coming_soon.html', {'tool_name': 'Repair PDF', 'tool_desc': 'Fix corrupted or damaged PDF files.'})
