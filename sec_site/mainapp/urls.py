from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from mainapp.views import *
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'mainapp'

urlpatterns = [
    # path('auth/jwt/create/', TokenObtainPairView.as_view()),
    # path('auth/jwt/refresh/', TokenRefreshView.as_view()),
    path('auth/jwt/create/', CustomTokenCreateView.as_view(), name="token_create"),
    path('auth/jwt/refresh/', CustomTokenRefreshView.as_view()),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/me/', GetMeView.as_view(), name='get_me'),
    path('auth/logout/', LogoutView.as_view()),
]

