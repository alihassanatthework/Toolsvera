from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from pypdf import PdfWriter, PdfReader
import uuid
import os
import io
import re
import tempfile
from django.conf import settings


def _tmp():
    # Serverless platforms (Vercel/AWS Lambda) only allow writes under /tmp.
    is_serverless = any(os.environ.get(k) for k in ('VERCEL', 'VERCEL_ENV', 'AWS_LAMBDA_FUNCTION_NAME', 'LAMBDA_TASK_ROOT'))
    base = '/tmp' if is_serverless else tempfile.gettempdir()
    tmp = os.path.join(base, 'toolsvera')
    os.makedirs(tmp, exist_ok=True)
    return tmp


def _safe_base(name, fallback='file'):
    if not name:
        return fallback
    base = os.path.basename(name)
    base, _ = os.path.splitext(base)
    base = re.sub(r'[^A-Za-z0-9._-]+', '_', base).strip('_') or fallback
    return base[:80]


def pdftools_home(request):
    return render(request, 'pdftools/home.html')


def pdf_merge(request):
    if request.method == 'POST':
        try:
            files = request.FILES.getlist('pdfs')
            if not files:
                return render(request, 'pdftools/merge.html', {'error': 'Please select at least two PDF files to merge.'})
            writer = PdfWriter()
            saved_paths = []
            for f in files:
                # Save each upload to /tmp so pypdf can stream it reliably
                p = os.path.join(_tmp(), f'{uuid.uuid4()}_{f.name}')
                with open(p, 'wb') as out:
                    for chunk in f.chunks():
                        out.write(chunk)
                saved_paths.append(p)
                writer.append(p)
            uid = str(uuid.uuid4())
            output_path = os.path.join(_tmp(), f'{uid}_merged.pdf')
            with open(output_path, 'wb') as out:
                writer.write(out)
            writer.close()
            base = _safe_base(files[0].name if files else 'document')
            fname = f'{base}_merged.pdf'
            response = FileResponse(open(output_path, 'rb'), as_attachment=True, filename=fname, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{fname}"'
            return response
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
            base = _safe_base(f.name)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=f'{base}_split.pdf')
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
            base = _safe_base(f.name)
            fname = f'{base}.docx'
            response = FileResponse(
                open(docx_path, 'rb'),
                as_attachment=True,
                filename=fname,
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            )
            response['Content-Disposition'] = f'attachment; filename="{fname}"'
            return response
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
            base = _safe_base(f.name)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=f'{base}_compressed.pdf')
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
            base = _safe_base(f.name)
            fname = f'{base}_pages.zip'
            response = FileResponse(open(zip_path, 'rb'), as_attachment=True, filename=fname, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{fname}"'
            return response
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
            base = _safe_base(files[0].name if files else 'images')
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=f'{base}.pdf')
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
            base = _safe_base(f.name)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=f'{base}_rotated.pdf')
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
            base = _safe_base(f.name)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=f'{base}_pages_removed.pdf')
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
            base = _safe_base(f.name)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=f'{base}_extracted.pdf')
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
            base = _safe_base(f.name)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=f'{base}_numbered.pdf')
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
            base = _safe_base(f.name)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=f'{base}_watermarked.pdf')
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
            base = _safe_base(f.name)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=f'{base}_protected.pdf')
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
            base = _safe_base(f.name)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=f'{base}_unlocked.pdf')
        except Exception as e:
            return render(request, 'pdftools/unlock.html', {'error': str(e)})
    return render(request, 'pdftools/unlock.html')


def pdf_organize(request):
    if request.method == 'POST':
        try:
            f = request.FILES['pdf']
            order_input = request.POST.get('order', '').strip()
            if not order_input:
                return render(request, 'pdftools/organize.html', {'error': 'Please enter a comma-separated list of page numbers (e.g. 3,1,2).'})
            if not re.fullmatch(r'\s*\d+(\s*,\s*\d+)*\s*', order_input):
                return render(request, 'pdftools/organize.html', {'error': 'Invalid format. Use comma-separated page numbers like 3,1,2.'})
            reader = PdfReader(f)
            total = len(reader.pages)
            try:
                order = [int(x.strip()) for x in order_input.split(',') if x.strip()]
            except ValueError:
                return render(request, 'pdftools/organize.html', {'error': 'Invalid page numbers.'})
            if len(set(order)) != len(order):
                return render(request, 'pdftools/organize.html', {'error': 'Duplicate page numbers are not allowed.'})
            for n in order:
                if n < 1 or n > total:
                    return render(request, 'pdftools/organize.html', {'error': f'Page {n} is out of range. PDF has {total} pages.'})
            writer = PdfWriter()
            for n in order:
                writer.add_page(reader.pages[n - 1])
            uid = str(uuid.uuid4())
            output_path = os.path.join(_tmp(), f'{uid}_organized.pdf')
            with open(output_path, 'wb') as out:
                writer.write(out)
            base = _safe_base(f.name)
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=f'{base}_organized.pdf')
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
    if request.method == 'POST':
        try:
            from reportlab.pdfgen import canvas as rlcanvas
            from reportlab.lib.colors import HexColor
            f = request.FILES['pdf']
            reader = PdfReader(f)
            writer = PdfWriter()
            # Parse repeating field arrays for overlays
            pages = request.POST.getlist('page[]')
            texts = request.POST.getlist('text[]')
            xs = request.POST.getlist('x[]')
            ys = request.POST.getlist('y[]')
            sizes = request.POST.getlist('size[]')
            colors = request.POST.getlist('color[]')
            overlays_by_page = {}
            for i in range(len(texts)):
                txt = (texts[i] or '').strip()
                if not txt:
                    continue
                try:
                    pg = int(pages[i]) - 1
                except Exception:
                    pg = 0
                overlays_by_page.setdefault(pg, []).append({
                    'text': txt,
                    'x': float(xs[i] or 50),
                    'y': float(ys[i] or 50),
                    'size': int(sizes[i] or 14),
                    'color': colors[i] or '#000000',
                })
            for idx, page in enumerate(reader.pages):
                if idx in overlays_by_page:
                    w = float(page.mediabox.width)
                    h = float(page.mediabox.height)
                    packet = io.BytesIO()
                    c = rlcanvas.Canvas(packet, pagesize=(w, h))
                    for ov in overlays_by_page[idx]:
                        try:
                            c.setFillColor(HexColor(ov['color']))
                        except Exception:
                            c.setFillColor(HexColor('#000000'))
                        c.setFont('Helvetica-Bold', ov['size'])
                        # x/y as percent from top-left; PDF origin is bottom-left
                        px = w * (ov['x'] / 100.0)
                        py = h - h * (ov['y'] / 100.0)
                        c.drawString(px, py, ov['text'])
                    c.save()
                    packet.seek(0)
                    overlay_pdf = PdfReader(packet)
                    page.merge_page(overlay_pdf.pages[0])
                writer.add_page(page)
            uid = str(uuid.uuid4())
            output_path = os.path.join(_tmp(), f'{uid}_edited.pdf')
            with open(output_path, 'wb') as out:
                writer.write(out)
            base = _safe_base(f.name)
            fname = f'{base}_edited.pdf'
            response = FileResponse(open(output_path, 'rb'), as_attachment=True, filename=fname, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{fname}"'
            return response
        except Exception as e:
            return render(request, 'pdftools/edit.html', {'error': str(e)})
    return render(request, 'pdftools/edit.html')


def pdf_repair(request):
    return render(request, 'coming_soon.html', {'tool_name': 'Repair PDF', 'tool_desc': 'Fix corrupted or damaged PDF files.'})
