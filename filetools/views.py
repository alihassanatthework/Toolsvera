from django.shortcuts import render
from django.http import FileResponse
import os
import uuid
import tempfile

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def word_to_pdf(request):
    if request.method == 'POST':
        try:
            f = request.FILES['docx']
            is_serverless = any(os.environ.get(k) for k in (
                'VERCEL', 'VERCEL_ENV', 'AWS_LAMBDA_FUNCTION_NAME', 'LAMBDA_TASK_ROOT'
            ))
            tmp = '/tmp/toolsvera' if is_serverless else os.path.join(tempfile.gettempdir(), 'toolsvera')
            os.makedirs(tmp, exist_ok=True)
            uid = str(uuid.uuid4())
            in_path = os.path.join(tmp, f'{uid}.docx')
            out_path = os.path.join(tmp, f'{uid}.pdf')
            with open(in_path, 'wb') as o:
                for c in f.chunks():
                    o.write(c)
            doc = Document(in_path)
            styles = getSampleStyleSheet()
            pdf = SimpleDocTemplate(out_path, pagesize=letter)
            elements = []
            for p in doc.paragraphs:
                if p.text.strip():
                    safe = p.text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    elements.append(Paragraph(safe, styles['Normal']))
                    elements.append(Spacer(1, 6))
            if not elements:
                elements.append(Paragraph('(Empty document)', styles['Normal']))
            pdf.build(elements)
            base = os.path.splitext(os.path.basename(f.name))[0]
            return FileResponse(
                open(out_path, 'rb'),
                as_attachment=True,
                filename=f'{base}.pdf',
                content_type='application/pdf',
            )
        except Exception as e:
            return render(request, 'filetools/word_to_pdf.html', {'error': str(e)})
    return render(request, 'filetools/word_to_pdf.html')
