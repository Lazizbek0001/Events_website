
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.url')),
    path('members/', include('django.contrib.auth.urls')),
    path('members/', include('members.urls')),
    path('', include('api.urls'))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# configure Admin titles

admin.site.site_header = "My CLub Adminstration page"
admin.site.site_title = "Browser Title"
admin.site.index_title = "Welcome to admin area"