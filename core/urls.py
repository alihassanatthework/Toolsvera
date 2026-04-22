from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('calculators.urls')),
    path('pdf-tools/', include('pdftools.urls')),
    path('files/', include('filetools.urls')),
    path('images/', include('imagetools.urls')),
    path('text/', include('texttools.urls')),
    path('sitemap.xml', TemplateView.as_view(
        template_name='sitemap.xml',
        content_type='application/xml'
    )),
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt',
        content_type='text/plain'
    )),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)