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
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .permissions import *
from django.shortcuts import get_object_or_404


# этот метод вызывается после регистрации юзера
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # после регистрации я юзеру сразу даю обычную роль
        try:
            usual_user = CustomRole.objects.get(title='usual_reader')
            usual_user.users.add(instance)
        except:
            pass


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

    def get(self, request, *args, **kwargs):
        user = request.user
        roles = []
        for role in user.roles.all():
            roles.append(role.id)
        return Response({'user': UserDetailSerializer(user, many=False).data, "roles": roles})


# подтверждение авторизации
class ConfirmLoginView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({"message": "Двухфакторка отключена"})

        # email = request.POST.get("email")
        # code = request.POST.get("code")
        #
        # # Удаляю все просроченные коды
        # codes = ConfirmLogin.objects.all()
        # for old_code in codes:
        #     timediff = datetime.now() - old_code.date_create
        #     if timediff.seconds >= conf_settings.CONFIRM_CODE_TIME:
        #         try:
        #             token = RefreshToken(token=old_code.refresh)
        #             token.blacklist()
        #         except:
        #             pass
        #         old_code.delete()
        #
        # if email is not None and code is not None:
        #     try:
        #         # проверяю почту и код
        #         user = User.objects.get(email=email)
        #         confirm = ConfirmLogin.objects.get(user=user, code=code)
        #         access = confirm.access
        #         refresh = confirm.refresh
        #         confirm.delete()
        #
        #         DeleteOldSessions()
        #
        #         # Получаю все сессии юзера
        #         warning = ""
        #         user_sessions = CustomSession.objects.filter(user=user)
        #         if len(user_sessions) >= conf_settings.SESSIONS_COUNT:
        #             warning = f"Предупреждение: вы превышаете кол-во допустимых сессий. Не считая эту, у вас {len(user_sessions)} активных сессии!"
        #
        #         # создаю новую сессию
        #         CustomSession.objects.create(user=user, token=refresh)
        #
        #         return Response({"access": access, "refresh": refresh, "warning": warning})
        #     except:
        #         return Response({"error": "Вы указали неверный код или он просрочен"})
        #
        # else:
        #     return Response({"message": "Вы не указали код"})


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


# Получить список книг
class GetBooksListView(APIView):
    # Это доступно вообще всем (даже неавторизованным)
    permission_classes = []

    def get(self, request, *args, **kwargs):
        books = Book.objects.all()
        return Response(BooksListSerializer(books, many=True).data)


# Прочитать конкретную книгу
class ReadBookView(APIView):
    # Прочитать конкретную книгу могут все авторизованные и с любым разрешением на чтение
    permission_classes = [IsAuthenticated, ReadForAll]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if pk:
            book = get_object_or_404(Book, pk=pk)
            return Response(BookDetailSerializer(book, many=False).data)


# создать книгу
class CreateBookView(APIView):
    # создать книгу могут все юзеры с любыми правами на создание
    permission_classes = [IsAuthenticated, CreateForAll]

    def post(self, request, *args, **kwargs):
        serializer = BookCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# изменить книгу
class ChangeBookView(APIView):
    # обновить книгу могут модеры или авторы
    permission_classes = [IsAuthenticated, BookAuthorOrAdmin]

    def put(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "pk не найден"})
        book = get_object_or_404(Book, pk=pk)
        serializer = BookCreateSerializer(data=request.data, instance=book, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "pk не найден"})
        book = get_object_or_404(Book, pk=pk)
        book.delete()
        return Response({'message': "удалено"})


# Роли
class RoleView(APIView):
    # Только для админа
    permission_classes = [IsAuthenticated, AdminOnly]

    # Список всех ролей
    def get(self, request, *args, **kwargs):
        roles = CustomRole.objects.all()
        return Response(RoleListSerializer(roles, many=True).data)

    # Создать новую роль
    def post(self, request, *args, **kwargs):
        serializer = RoleCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# Изменить роль
class ChangeRoleView(APIView):
    # Только для админа
    permission_classes = [IsAuthenticated, AdminOnly]

    def put(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "pk не найден"})
        role = get_object_or_404(CustomRole, pk=pk)
        serializer = RoleCreateSerializer(data=request.data, instance=role, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "pk не найден"})
        role = get_object_or_404(CustomRole, pk=pk)
        role.delete()
        return Response({'message': "удалено"})


# Добавление/удаление юзеров в роль
class RoleUserView(APIView):
    # Только для админа
    permission_classes = [IsAuthenticated, AdminOnly]

    # добавить юзеров в роль
    def post(self, request, *args, **kwargs):
        pk = request.data["role"]
        users = request.data["users"]
        role = get_object_or_404(CustomRole, pk=pk)
        for user_id in users:
            user = get_object_or_404(User, pk=user_id)
            role.users.add(user)
        return Response({"message": "yes"})

    # убрать у юзера роль
    def delete(self, request, *args, **kwargs):
        pk = request.data["role"]
        users = request.data["users"]
        role = get_object_or_404(CustomRole, pk=pk)
        for user_id in users:
            user = get_object_or_404(User, pk=user_id)
            role.users.remove(user)
        return Response({"message": "yes"})


# Разрешения
class PermissionView(APIView):
    # Только для админа
    permission_classes = [IsAuthenticated, AdminOnly]

    # Список всех разрешений
    def get(self, request, *args, **kwargs):
        permissions = CustomPermission.objects.all()
        return Response(PermissonSerializer(permissions, many=True).data)

    # Создать новое разрешение
    def post(self, request, *args, **kwargs):
        serializer = PermissonSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# Изменить разрешение
class ChangePermissionView(APIView):
    # Только для админа
    permission_classes = [IsAuthenticated, AdminOnly]

    def put(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "pk не найден"})
        permission = get_object_or_404(CustomPermission, pk=pk)
        serializer = PermissonSerializer(data=request.data, instance=permission, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "pk не найден"})
        permission = get_object_or_404(CustomPermission, pk=pk)
        permission.delete()
        return Response({'message': "удалено"})
