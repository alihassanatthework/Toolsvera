from django.urls import path
from . import views

app_name = 'pdftools'

urlpatterns = [
    path('', views.pdftools_home, name='home'),
    path('merge-pdf/', views.pdf_merge, name='merge'),
    path('split-pdf/', views.pdf_split, name='split'),
    path('pdf-to-word/', views.pdf_to_word, name='to_word'),
    path('compress-pdf/', views.pdf_compress, name='compress'),
    path('pdf-to-jpg/', views.pdf_to_jpg, name='to_jpg'),
    path('jpg-to-pdf/', views.jpg_to_pdf, name='jpg_to_pdf'),
    path('rotate-pdf/', views.pdf_rotate, name='rotate'),
    path('remove-pages-from-pdf/', views.pdf_remove_pages, name='remove_pages'),
    path('extract-pages-from-pdf/', views.pdf_extract_pages, name='extract_pages'),
    path('add-page-numbers-to-pdf/', views.pdf_add_page_numbers, name='add_page_numbers'),
    path('watermark-pdf/', views.pdf_watermark, name='watermark'),
    path('protect-pdf/', views.pdf_protect, name='protect'),
    path('unlock-pdf/', views.pdf_unlock, name='unlock'),
    path('organize-pdf/', views.pdf_organize, name='organize'),
    # Coming Soon
    path('pdf-to-powerpoint/', views.pdf_to_powerpoint, name='to_powerpoint'),
    path('pdf-to-excel/', views.pdf_to_excel, name='to_excel'),
    path('powerpoint-to-pdf/', views.powerpoint_to_pdf, name='powerpoint_to_pdf'),
    path('excel-to-pdf/', views.excel_to_pdf, name='excel_to_pdf'),
    path('html-to-pdf/', views.html_to_pdf, name='html_to_pdf'),
    path('pdf-ocr/', views.pdf_ocr, name='ocr'),
    path('pdf-sign/', views.pdf_sign, name='sign'),
    path('pdf-edit/', views.pdf_edit, name='edit'),
    path('pdf-edit/extract/', views.pdf_edit_extract, name='edit_extract'),
    path('pdf-repair/', views.pdf_repair, name='repair'),
]
