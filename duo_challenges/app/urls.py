from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Alle websitepagina's staan in de challenges app.
    path('', include('challenges.urls')),
]
