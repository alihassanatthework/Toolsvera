# ToolsVera

A free, open-source multi-tool productivity platform built with Django.
Inspired by platforms like ilovepdf, smallpdf, and calculator.net.

---

## Features

### Calculators
- BMI Calculator
- Percentage Calculator
- Mortgage / Loan Calculator

### PDF Tools
- Merge PDFs
- Split PDF
- PDF to Word conversion
- Compress PDF (coming soon)

### File Tools
- Word (.docx) to PDF conversion

### Image Tools
- Image format converter (JPG, PNG, WEBP, BMP)
- Image resizer

---

## Tech Stack

| Layer        | Technology                        |
|--------------|-----------------------------------|
| Backend      | Django 6.x (Python 3.14)          |
| Frontend     | Tailwind CSS (CDN)                |
| Database     | SQLite (dev) / PostgreSQL (prod)  |
| Task Queue   | Celery + Redis                    |
| File Storage | Local media / AWS S3 (prod)       |
| PDF Engine   | pypdf, pdf2docx, reportlab        |
| Image Engine | Pillow                            |
| Doc Engine   | python-docx, LibreOffice          |

---

## Project Structure
myplatform/
├── core/               # Django settings, urls, wsgi
├── calculators/        # Calculator tools app
├── filetools/          # File conversion app
├── pdftools/           # PDF tools app
├── imagetools/         # Image tools app
├── templates/          # All HTML templates
│   ├── base.html
│   ├── home.html
│   ├── calculators/
│   ├── pdftools/
│   ├── filetools/
│   └── imagetools/
├── static/             # CSS, JS, images
├── media/              # Uploaded & converted files
├── venv/               # Python virtual environment
└── manage.py

---

## Local Setup (macOS)

### 1. Clone or enter the project
```bash
cd /Users/yourname/Desktop/calculator/myplatform
```

### 2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install django djangorestframework celery redis pillow
pip install python-docx PyPDF2 pdf2docx reportlab pypdf
pip install django-storages boto3 psycopg2-binary gunicorn
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Create admin user
```bash
python manage.py createsuperuser
```

### 6. Start the server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

---

## Running Celery (for file conversions)

Open a second terminal tab:
```bash
source venv/bin/activate
celery -A core worker --loglevel=info
```

---

## Services Required

| Service      | macOS Install Command              |
|--------------|------------------------------------|
| PostgreSQL   | `brew install postgresql@15`       |
| Redis        | `brew install redis`               |
| LibreOffice  | `brew install --cask libreoffice`  |

---

## Roadmap

- [ ] Age calculator
- [ ] Scientific calculator
- [ ] Unit converter
- [ ] PDF editor (in-browser)
- [ ] Image cropper
- [ ] QR code generator
- [ ] Password generator
- [ ] Word count tool
- [ ] User accounts & history
- [ ] Dark/light mode toggle
- [ ] REST API for all tools

---

## License

MIT License — free to use, modify, and distribute.

---

## Author

Built by Ali Hassan  
Platform: ToolsVera  
Stack: Django + Tailwind CSS