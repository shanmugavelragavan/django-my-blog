from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # The path to your blog app's URLs.
    # Since blog/urls.py defines app_name = "blog", this makes the "blog" namespace available.
    path('', include('blog.urls')),
    path('admin/', admin.site.urls),
]

# The following block for serving media files in development mode
# is now correctly appended to the urlpatterns defined above.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Note: If 'django.contrib.staticfiles' is in your INSTALLED_APPS,
    # the development server (manage.py runserver) automatically serves static files
    # from your app's 'static' directories and any directories listed in STATICFILES_DIRS.
    # Explicitly adding static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # is generally not needed for 'runserver' but might be used in other deployment scenarios.