from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
User = get_user_model()
from .serializers import *
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .models import *
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class CustomTokenCreateView(TokenObtainPairView):
    serializer_class = CustomTokenCreateSerializer








# class RefreshToken(APIView):
#     @staticmethod
#     def post(request, *args, **kwargs):
#         tokenr = TokenObtainPairSerializer().get_token(request.user)
#         tokena = AccessToken().for_user(request.user)
#         {"refresh": str(tokenr), "access": str(tokena)}


# Регистрация пользователя
class RegisterView(APIView):
    @staticmethod
    def post(request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'user': serializer.data})


# Получение информации о себе
class GetMeView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request, *args, **kwargs):
        user = request.user
        return Response({'user': UserDetailSerializer(user, many=False).data})


# Logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = self.request.data.get('refresh')
        token = RefreshToken(token=refresh_token)
        token.blacklist()
        session = CustomSession.objects.get(token=refresh_token)
        session.delete()
        return Response({"status": "OK, goodbye"})

    # def post(self, request, *args, **kwargs):
    #     if self.request.data.get('all'):
    #         token: OutstandingToken
    #         for token in OutstandingToken.objects.filter(user=request.user):
    #             _, _ = BlacklistedToken.objects.get_or_create(token=token)
    #         return Response({"status": "OK, goodbye, all refresh tokens blacklisted"})
    #     refresh_token = self.request.data.get('refresh_token')
    #     token = RefreshToken(token=refresh_token)
    #     token.blacklist()
    #     return Response({"status": "OK, goodbye"})




