from rest_framework import permissions
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import *
from django.shortcuts import get_object_or_404


# Вообще все могут прочитать, у кого есть любое разрешение на чтение
class ReadForAll(permissions.BasePermission):
    def has_permission(self, request, view):
        user_permissions = get_user_permissions(request.user)
        if "read_all" in user_permissions or "read_access" in user_permissions:
            return True
        else:
            return False


# Вообще все могут создать, у кого есть любое разрешение на создание
class CreateForAll(permissions.BasePermission):
    def has_permission(self, request, view):
        user_permissions = get_user_permissions(request.user)
        if "create_all" in user_permissions or "create_access" in user_permissions:
            return True
        else:
            return False


# Только автор или модер (кто имеет put_all)
class BookAuthorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user_permissions = get_user_permissions(request.user)
        book = get_object_or_404(Book, pk=view.kwargs['pk'])
        SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']
        if request.method == "PUT" or request.method == "PATCH":
            if "put_all" in user_permissions or ("put_access" in user_permissions and request.user in book.authors.all()):
                return True
            else:
                return False
        elif request.method == "DELETE":
            if "delete_all" in user_permissions or ("delete_access" in user_permissions and request.user in book.authors.all()):
                return True
            else:
                return False
        elif request.method == "POST":
            if "create_all" in user_permissions or ("create_access" in user_permissions and request.user in book.authors.all()):
                return True
            else:
                return False
        elif request.method in SAFE_METHODS:
            if "read_all" in user_permissions or ("read_access" in user_permissions and request.user in book.authors.all()):
                return True
            else:
                return False


# Вообще все могут создать, у кого есть любое разрешение на создание
class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        admin = CustomRole.objects.get(title="admin")
        if admin in request.user.roles.all():
            return True
        else:
            return False


# получить все разрешения всех ролей юзера
def get_user_permissions(user):
    roles = user.roles.all()
    user_permissions = []
    for role in roles:
        role_permissions = role.permissions.all()
        for role_permission in role_permissions:
            if role_permission.title not in user_permissions:
                user_permissions.append(role_permission.title)

    return user_permissions
