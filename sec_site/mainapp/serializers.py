from datetime import datetime
from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenObtainPairSerializer
from rest_framework import serializers
import django.contrib.auth.password_validation as validators
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from .models import ConfirmLogin
from django.conf import settings as conf_settings
from random import randrange
from django.core.mail import EmailMessage
from .models import CustomSession


# Создание (регистрация) юзера
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password']

    def validate_password(self, data):
        validators.validate_password(password=data, user=User)
        return data


# Отображение информации о юзере
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


# Кастомное создание токенов
class CustomTokenCreateSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(CustomTokenCreateSerializer, self).validate(attrs)
        user = User.objects.get(email=attrs['email'])
        old_codes = ConfirmLogin.objects.filter(user=user)

        # Удаляю все старые коды этого юзера, если они есть
        for old_code in old_codes:
            try:
                token = RefreshToken(token=old_code.refresh)
                token.blacklist()
            except:
                pass
            old_code.delete()

        # Удаляю все просроченные коды
        codes = ConfirmLogin.objects.all()
        for code in codes:
            timediff = datetime.now() - code.date_create
            if timediff.seconds >= conf_settings.CONFIRM_CODE_TIME:
                try:
                    token = RefreshToken(token=code.refresh)
                    token.blacklist()
                except:
                    pass
                code.delete()

        # Генерирую новый уникальный код
        codes = ConfirmLogin.objects.all()
        codes_list = []
        for code in codes:
            codes_list.append(code.code)
        new_code = 0
        for _ in range(6):
            new_code = new_code*10 + randrange(10)
        while new_code in codes_list:
            new_code = 0
            for _ in range(6):
                new_code = new_code * 10 + randrange(10)

        ConfirmLogin.objects.create(user=user, code=new_code, access=data['access'], refresh=data['refresh'])

        try:
            theme = f'Авторизация на сайте'  # тема письма
            mail_content = f"Ваш код: {new_code}"  # содержание
            who = user.email  # кому
            mail = EmailMessage(theme, mail_content, conf_settings.EMAIL_HOST_USER, [who])
            mail.send()
            return {"message": "Вам на почту был отправлен код"}

        except:
            return {"error": "Не получилось отправить код авторизации на почту"}


# Кастомное обновление токенов
class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super(CustomTokenRefreshSerializer, self).validate(attrs)

        # удаляю все просроченные сессии
        sessions = CustomSession.objects.all()
        for session in sessions:
            try:
                UntypedToken(session.token)
                # если мы здесь, значит токен не просрочен и сессия активна
            except:
                # если мы здесь, значит токен просрочен, и сессия неактивна
                session.delete()

        # нахожу старую сессию по токену и обновляю
        this_session = CustomSession.objects.get(token=attrs['refresh'])
        this_session.token = data['refresh']
        this_session.date_create = datetime.now()
        this_session.save()

        return data
