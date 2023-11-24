from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import include, path, re_path


try:  # Place build info into html header of Admin panel
    with open(settings.BASE_DIR / 'buildinfo') as f:
        admin.site.site_header = mark_safe(f'Django administration <small>({f.read()})</small>')
except Exception:
    pass


urlpatterns = [
    path('', include('blog.urls')),
    path('', include('common.urls')),
    path('', include('account.urls')),
    path('', include('api_property.urls')),
    path('', include('rent_analyzer.urls')),
    path('', include('sale_estimator.urls')),
    path('', include('search.urls')),
    path('', include('reports.urls')),
    path('admin/', admin.site.urls),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:  # for DRF browsable UI
    urlpatterns += [path('api/drfurls/', include('rest_framework.urls')),]
