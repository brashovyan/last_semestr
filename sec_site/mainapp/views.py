from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.conf import settings as conf_settings
User = get_user_model()
from datetime import datetime
from .models import *


# Удаление старых сессий
def DeleteOldSessions():
    # удаляю все просроченные сессии
    sessions = CustomSession.objects.all()
    for session in sessions:
        try:
            UntypedToken(session.token)
            # если мы здесь, значит токен не просрочен и сессия активна
        except:
            # если мы здесь, значит токен просрочен, и сессия неактивна
            session.delete()


# Кастомное обновление токена
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


# Кастомное создание токена
class CustomTokenCreateView(TokenObtainPairView):
    serializer_class = CustomTokenCreateSerializer


# Получение информации о себе
class GetMeView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request, *args, **kwargs):
        user = request.user
        return Response({'user': UserDetailSerializer(user, many=False).data})


# подтверждение авторизации
class ConfirmLoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        code = request.POST.get("code")

        # Удаляю все просроченные коды
        codes = ConfirmLogin.objects.all()
        for old_code in codes:
            timediff = datetime.now() - old_code.date_create
            if timediff.seconds >= conf_settings.CONFIRM_CODE_TIME:
                try:
                    token = RefreshToken(token=old_code.refresh)
                    token.blacklist()
                except:
                    pass
                old_code.delete()

        if email is not None and code is not None:
            try:
                # проверяю почту и код
                user = User.objects.get(email=email)
                confirm = ConfirmLogin.objects.get(user=user, code=code)
                access = confirm.access
                refresh = confirm.refresh
                confirm.delete()

                DeleteOldSessions()

                # Получаю все сессии юзера
                warning = ""
                user_sessions = CustomSession.objects.filter(user=user)
                if len(user_sessions) >= conf_settings.SESSIONS_COUNT:
                    warning = f"Предупреждение: вы превышаете кол-во допустимых сессий. Не считая эту, у вас {len(user_sessions)} активных сессии!"

                # создаю новую сессию
                CustomSession.objects.create(user=user, token=refresh)

                return Response({"access": access, "refresh": refresh, "warning": warning})
            except:
                return Response({"message": "Вы указали неверный код или он просрочен"})

        else:
            return Response({"message": "Вы не указали код"})


# Logout
class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = self.request.data.get('refresh')
        try:
            token = RefreshToken(token=refresh_token)
            token.blacklist()
            session = CustomSession.objects.get(token=refresh_token)
            session.delete()
            return Response({"status": "OK, goodbye"})
        except:
            return Response({"error": "неверный токен"})


# Logout из всех сессий кроме текущей
class LogoutAllView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        refresh_token = self.request.data.get('refresh')

        DeleteOldSessions()

        user_sessions = CustomSession.objects.filter(user=request.user)
        for session in user_sessions:
            if session.token != refresh_token:
                token = RefreshToken(token=session.token)
                token.blacklist()
                session.delete()

        return Response({"message": "OK, goodbye"})


# получить все действующие сессии
class GetSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        DeleteOldSessions()

        user_sessions = CustomSession.objects.filter(user=request.user)
        sessions = {}
        i = 1
        for session in user_sessions:
            data = {f"session {i}": session.token}
            sessions.update(data)
            i += 1

        return Response(sessions)
