from django.contrib import admin
from django.urls import path, include

from starwars.views import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('knockknock/', health_check, name='knockknock'),
    path('core/', include('core.urls')),
]
