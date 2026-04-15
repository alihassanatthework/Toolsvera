from django.shortcuts import render
from django.http import FileResponse
import uuid
import os
import subprocess
from django.conf import settings


def word_to_pdf(request):
    if request.method == 'POST':
        f = request.FILES['docx']
        uid = str(uuid.uuid4())
        tmp = os.path.join(settings.MEDIA_ROOT, 'tmp')
        os.makedirs(tmp, exist_ok=True)
        docx_path = os.path.join(tmp, f'{uid}.docx')
        with open(docx_path, 'wb') as out:
            for chunk in f.chunks():
                out.write(chunk)
        subprocess.run([
            'libreoffice', '--headless', '--convert-to', 'pdf',
            '--outdir', tmp, docx_path
        ])
        pdf_path = os.path.join(tmp, f'{uid}.pdf')
        return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename='converted.pdf')
    return render(request, 'filetools/word_to_pdf.html')