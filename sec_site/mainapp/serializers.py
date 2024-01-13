from rest_framework import serializers
import django.contrib.auth.password_validation as validators
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenObtainPairSerializer
from .models import CustomSession



class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password']

    def validate_password(self, data):
        validators.validate_password(password=data, user=User)
        return data


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class CustomTokenCreateSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(CustomTokenCreateSerializer, self).validate(attrs)
        user = User.objects.get(email=attrs['email'])
        CustomSession.objects.create(user=user, token=data['refresh'])
        # print("Я создал токены")
        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super(CustomTokenRefreshSerializer, self).validate(attrs)
        session = CustomSession.objects.get(token=attrs['refresh'])
        session.token = data['refresh']
        session.save()
        # print(f"Старый {attrs['refresh']}")
        # print(f"Новый {data['refresh']}")
        return data
