from django.shortcuts import render
from django.http import FileResponse
from pypdf import PdfWriter, PdfReader
import uuid
import os
from django.conf import settings


def pdf_merge(request):
    if request.method == 'POST':
        files = request.FILES.getlist('pdfs')
        writer = PdfWriter()
        for f in files:
            reader = PdfReader(f)
            for page in reader.pages:
                writer.add_page(page)
        uid = str(uuid.uuid4())
        tmp = os.path.join(settings.MEDIA_ROOT, 'tmp')
        os.makedirs(tmp, exist_ok=True)
        output_path = os.path.join(tmp, f'{uid}_merged.pdf')
        with open(output_path, 'wb') as out:
            writer.write(out)
        return FileResponse(open(output_path, 'rb'), as_attachment=True, filename='merged.pdf')
    return render(request, 'pdftools/merge.html')


def pdf_split(request):
    if request.method == 'POST':
        f = request.FILES['pdf']
        reader = PdfReader(f)
        uid = str(uuid.uuid4())
        tmp = os.path.join(settings.MEDIA_ROOT, 'tmp')
        os.makedirs(tmp, exist_ok=True)
        output_path = os.path.join(tmp, f'{uid}_page1.pdf')
        writer = PdfWriter()
        writer.add_page(reader.pages[0])
        with open(output_path, 'wb') as out:
            writer.write(out)
        return FileResponse(open(output_path, 'rb'), as_attachment=True, filename='page1.pdf')
    return render(request, 'pdftools/split.html')


def pdf_to_word(request):
    if request.method == 'POST':
        from pdf2docx import Converter
        f = request.FILES['pdf']
        uid = str(uuid.uuid4())
        tmp = os.path.join(settings.MEDIA_ROOT, 'tmp')
        os.makedirs(tmp, exist_ok=True)
        pdf_path = os.path.join(tmp, f'{uid}.pdf')
        docx_path = os.path.join(tmp, f'{uid}.docx')
        with open(pdf_path, 'wb') as out:
            for chunk in f.chunks():
                out.write(chunk)
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        return FileResponse(open(docx_path, 'rb'), as_attachment=True, filename='converted.docx')
    return render(request, 'pdftools/to_word.html')


def pdf_compress(request):
    return render(request, 'pdftools/compress.html')