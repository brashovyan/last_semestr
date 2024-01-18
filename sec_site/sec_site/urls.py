from django.contrib import admin
from django.urls import path, include
from .yasg import urlpatterns as doc_urls


urlpatterns = [
    path('api/v1/admin/', admin.site.urls),
    path("api/v1/", include("mainapp.urls")),
]

# автоматическая документация (swagger, redoc)
urlpatterns += doc_urls
