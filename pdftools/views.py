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


def pdf_edit_extract(request):
    """POST a PDF, get back JSON {html} of editable content."""
    from django.http import JsonResponse
    if request.method != 'POST' or 'pdf' not in request.FILES:
        return JsonResponse({'error': 'POST a PDF as `pdf`.'}, status=400)
    try:
        from pdf2docx import Converter
        import mammoth
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
        with open(docx_path, 'rb') as docx_f:
            result = mammoth.convert_to_html(docx_f)
            html = result.value or ''
        if not html.strip():
            html = '<p>(No editable text extracted. The PDF may be a scan.)</p>'
        return JsonResponse({'html': html, 'name': _safe_base(f.name)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def _html_to_pdf_bytes(html_str):
    """Render Quill-style HTML to a PDF byte string using ReportLab Platypus."""
    from html.parser import HTMLParser
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, ListFlowable, ListItem
    import io as _io

    styles = getSampleStyleSheet()
    base = styles['BodyText']
    base.fontSize = 11; base.leading = 15
    H = {
        1: ParagraphStyle('H1', parent=styles['Heading1'], fontSize=22, leading=26, spaceAfter=10),
        2: ParagraphStyle('H2', parent=styles['Heading2'], fontSize=18, leading=22, spaceAfter=8),
        3: ParagraphStyle('H3', parent=styles['Heading3'], fontSize=14, leading=18, spaceAfter=6),
    }

    flowables = []

    class P(HTMLParser):
        TAG_MAP = {'strong': 'b', 'b': 'b', 'em': 'i', 'i': 'i', 'u': 'u', 's': 'strike', 'strike': 'strike', 'br': 'br'}
        def __init__(self):
            super().__init__()
            self.stack = []  # list of (tag, opening_str)
            self.buf = []    # current paragraph inline content
            self.block = None  # current block tag (p, h1..h3, li)
            self.list_items = []  # accumulated <li> content while in list
            self.list_type = None  # 'ul' or 'ol'
            self.align = TA_LEFT
        def _open(self, tag, attrs):
            attrs = dict(attrs)
            style = attrs.get('style', '') or ''
            # span/font handling
            if tag == 'span' or tag == 'font':
                bits = []
                color = None; size = None
                for piece in style.split(';'):
                    if ':' not in piece: continue
                    k, v = [x.strip() for x in piece.split(':', 1)]
                    if k == 'color': color = v
                    if k == 'background-color' and v.lower() not in ('transparent','#fff','#ffffff','white'):
                        # highlight: emulate with font color shift is wrong; ignore for now
                        pass
                    if k == 'font-size':
                        size = v.replace('px','').replace('pt','').strip()
                if color:
                    self.buf.append(f'<font color="{color}">'); self.stack.append('</font>')
                if size:
                    try: int(float(size))
                    except: size = None
                if size:
                    self.buf.append(f'<font size="{size}">'); self.stack.append('</font>')
                return
            mapped = self.TAG_MAP.get(tag)
            if mapped:
                self.buf.append(f'<{mapped}/>' if mapped == 'br' else f'<{mapped}>')
                if mapped != 'br': self.stack.append(f'</{mapped}>')
        def _close(self, tag):
            if tag in ('span', 'font'):
                # pop any stacked closers that were opened by this span
                while self.stack and self.stack[-1] in ('</font>',):
                    self.buf.append(self.stack.pop())
                return
            mapped = self.TAG_MAP.get(tag)
            if mapped and mapped != 'br' and self.stack:
                close = f'</{mapped}>'
                # find and pop matching
                if close in self.stack:
                    while self.stack:
                        c = self.stack.pop()
                        self.buf.append(c)
                        if c == close: break
        def _flush_para(self, style=None):
            text = ''.join(self.buf).strip()
            self.buf = []
            self.stack = []
            if not text: return
            st = style or base
            if self.align != TA_LEFT:
                st = ParagraphStyle('al', parent=st, alignment=self.align)
            try:
                flowables.append(Paragraph(text, st))
                flowables.append(Spacer(1, 4))
            except Exception:
                # last-resort: strip tags
                import re as _re
                flowables.append(Paragraph(_re.sub(r'<[^>]+>', '', text), st))
                flowables.append(Spacer(1, 4))
        def handle_starttag(self, tag, attrs):
            attrs_d = dict(attrs)
            style = (attrs_d.get('style') or '').lower()
            if 'text-align:right' in style: self.align = TA_RIGHT
            elif 'text-align:center' in style: self.align = TA_CENTER
            elif 'text-align:justify' in style: self.align = TA_JUSTIFY
            elif 'text-align:left' in style: self.align = TA_LEFT
            if tag in ('p','div'):
                self.block = 'p'
            elif tag in ('h1','h2','h3'):
                self.block = tag
            elif tag == 'ul':
                self.list_type = 'ul'; self.list_items = []
            elif tag == 'ol':
                self.list_type = 'ol'; self.list_items = []
            elif tag == 'li':
                self.block = 'li'; self.buf = []; self.stack = []
            elif tag == 'br':
                self.buf.append('<br/>')
            elif tag == 'hr':
                flowables.append(Spacer(1, 6))
            else:
                self._open(tag, attrs)
        def handle_endtag(self, tag):
            if tag in ('p','div'):
                self._flush_para()
                self.block = None
                self.align = TA_LEFT
            elif tag in ('h1','h2','h3'):
                self._flush_para(H.get(int(tag[1]), base))
                self.block = None
                self.align = TA_LEFT
            elif tag == 'li':
                text = ''.join(self.buf).strip()
                self.buf = []; self.stack = []
                if text:
                    self.list_items.append(Paragraph(text, base))
                self.block = None
            elif tag in ('ul','ol'):
                if self.list_items:
                    flowables.append(ListFlowable(
                        [ListItem(p) for p in self.list_items],
                        bulletType='1' if tag == 'ol' else 'bullet',
                        leftIndent=18,
                    ))
                    flowables.append(Spacer(1, 4))
                self.list_items = []; self.list_type = None
            else:
                self._close(tag)
        def handle_data(self, data):
            if not self.block and not self.list_type:
                if data.strip():
                    self.block = 'p'
                    self.buf.append(self._esc(data))
            else:
                self.buf.append(self._esc(data))
        @staticmethod
        def _esc(s):
            return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))

    parser = P()
    parser.feed(html_str or '')
    parser._flush_para()

    buf = _io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            leftMargin=0.75*inch, rightMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    if not flowables:
        flowables = [Paragraph('(Empty document)', base)]
    doc.build(flowables)
    return buf.getvalue()


def pdf_edit(request):
    """GET: render editor. POST with `mode=export`: HTML → PDF download. Legacy overlay mode also supported."""
    if request.method == 'POST':
        try:
            mode = request.POST.get('mode', 'overlay')
            if mode == 'export':
                html_str = request.POST.get('html', '')
                name = _safe_base(request.POST.get('name') or 'edited')
                pdf_bytes = _html_to_pdf_bytes(html_str)
                uid = str(uuid.uuid4())
                output_path = os.path.join(_tmp(), f'{uid}_edited.pdf')
                with open(output_path, 'wb') as out:
                    out.write(pdf_bytes)
                fname = f'{name}_edited.pdf'
                response = FileResponse(open(output_path, 'rb'), as_attachment=True, filename=fname, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{fname}"'
                return response
            # ── legacy overlay path (kept for compatibility) ──
            import json
            from reportlab.pdfgen import canvas as rlcanvas
            from reportlab.lib.colors import HexColor, white
            f = request.FILES['pdf']
            reader = PdfReader(f)
            writer = PdfWriter()
            edits = []
            edits_raw = request.POST.get('edits_json', '').strip()
            if edits_raw:
                try:
                    edits = json.loads(edits_raw)
                except Exception:
                    edits = []
            by_page = {}
            for ed in edits:
                try:
                    pg = int(ed.get('page', 1)) - 1
                except Exception:
                    pg = 0
                by_page.setdefault(pg, []).append(ed)
            for idx, page in enumerate(reader.pages):
                if idx in by_page:
                    w = float(page.mediabox.width)
                    h = float(page.mediabox.height)
                    packet = io.BytesIO()
                    c = rlcanvas.Canvas(packet, pagesize=(w, h))
                    for ed in by_page[idx]:
                        kind = ed.get('type', 'add')
                        text = (ed.get('text') or '').strip()
                        if not text:
                            continue
                        size = float(ed.get('size') or 14)
                        try:
                            fill = HexColor(ed.get('color') or '#000000')
                        except Exception:
                            fill = HexColor('#000000')
                        if kind == 'edit':
                            # PDF-space coords (origin bottom-left)
                            px = float(ed.get('x', 0))
                            py = float(ed.get('y', 0))  # baseline
                            ow = float(ed.get('w', 0))
                            # White rectangle to cover the original glyphs
                            pad = max(1.5, size * 0.08)
                            c.setFillColor(white)
                            c.rect(px - pad, py - pad, ow + pad * 2, size + pad * 2, stroke=0, fill=1)
                            # Overlay new text at the same baseline
                            c.setFillColor(fill)
                            c.setFont('Helvetica', size)
                            c.drawString(px, py, text)
                        else:
                            # 'add' uses percent coords from top-left of page
                            xp = float(ed.get('xPct', ed.get('x', 50)))
                            yp = float(ed.get('yPct', ed.get('y', 50)))
                            c.setFillColor(fill)
                            c.setFont('Helvetica-Bold', size)
                            c.drawString(w * (xp / 100.0), h - h * (yp / 100.0), text)
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
