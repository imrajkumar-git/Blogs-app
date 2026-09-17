from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/blog/", include("blog.urls")),
    path("api/reviews/", include("reviews.urls")),
]

if settings.DEBUG:
    # Serve uploaded avatars and blog cover images during local development.
    # In production, serve MEDIA from your web server or object storage
    # (S3, Cloudflare R2, etc.) instead of through Django.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
