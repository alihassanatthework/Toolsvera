from django.urls import path
from . import views

app_name = 'pdftools'

urlpatterns = [
    path('merge/', views.pdf_merge, name='merge'),
    path('split/', views.pdf_split, name='split'),
    path('to-word/', views.pdf_to_word, name='to_word'),
    path('compress/', views.pdf_compress, name='compress'),
    path('to-jpg/', views.pdf_to_jpg, name='to_jpg'),
    path('jpg-to-pdf/', views.jpg_to_pdf, name='jpg_to_pdf'),
    path('rotate/', views.pdf_rotate, name='rotate'),
    path('remove-pages/', views.pdf_remove_pages, name='remove_pages'),
    path('extract-pages/', views.pdf_extract_pages, name='extract_pages'),
    path('add-page-numbers/', views.pdf_add_page_numbers, name='add_page_numbers'),
    path('watermark/', views.pdf_watermark, name='watermark'),
    path('protect/', views.pdf_protect, name='protect'),
    path('unlock/', views.pdf_unlock, name='unlock'),
    path('organize/', views.pdf_organize, name='organize'),
    # Coming Soon
    path('to-powerpoint/', views.pdf_to_powerpoint, name='to_powerpoint'),
    path('to-excel/', views.pdf_to_excel, name='to_excel'),
    path('powerpoint-to-pdf/', views.powerpoint_to_pdf, name='powerpoint_to_pdf'),
    path('excel-to-pdf/', views.excel_to_pdf, name='excel_to_pdf'),
    path('html-to-pdf/', views.html_to_pdf, name='html_to_pdf'),
    path('ocr/', views.pdf_ocr, name='ocr'),
    path('sign/', views.pdf_sign, name='sign'),
    path('edit/', views.pdf_edit, name='edit'),
    path('repair/', views.pdf_repair, name='repair'),
]
