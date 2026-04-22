from django.urls import path
from . import views

app_name = 'pdftools'

urlpatterns = [
    path('pdf-merge/', views.pdf_merge, name='merge'),
    path('pdf-split/', views.pdf_split, name='split'),
    path('pdf-to-word/', views.pdf_to_word, name='to_word'),
    path('compress-pdf/', views.pdf_compress, name='compress'),
    path('pdf-to-jpg/', views.pdf_to_jpg, name='to_jpg'),
    path('jpg-to-pdf/', views.jpg_to_pdf, name='jpg_to_pdf'),
    path('pdf-rotate/', views.pdf_rotate, name='rotate'),
    path('pdf-remove-pages/', views.pdf_remove_pages, name='remove_pages'),
    path('pdf-extract-pages/', views.pdf_extract_pages, name='extract_pages'),
    path('pdf-add-page-numbers/', views.pdf_add_page_numbers, name='add_page_numbers'),
    path('pdf-watermark/', views.pdf_watermark, name='watermark'),
    path('pdf-protection/', views.pdf_protect, name='protect'),
    path('pdf-unlock/', views.pdf_unlock, name='unlock'),
    path('pdf-organize/', views.pdf_organize, name='organize'),
    # Coming Soon
    path('pdf-to-powerpoint/', views.pdf_to_powerpoint, name='to_powerpoint'),
    path('pdf-to-excel/', views.pdf_to_excel, name='to_excel'),
    path('powerpoint-to-pdf/', views.powerpoint_to_pdf, name='powerpoint_to_pdf'),
    path('excel-to-pdf/', views.excel_to_pdf, name='excel_to_pdf'),
    path('html-to-pdf/', views.html_to_pdf, name='html_to_pdf'),
    path('pdf-ocr/', views.pdf_ocr, name='ocr'),
    path('pdf-sign/', views.pdf_sign, name='sign'),
    path('pdf-edit/', views.pdf_edit, name='edit'),
    path('pdf-repair/', views.pdf_repair, name='repair'),
]
