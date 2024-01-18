from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager


# Настройка создания кастомного юзера
class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = User(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        assert extra_fields['is_staff']
        assert extra_fields['is_superuser']
        assert extra_fields['is_active']
        return self._create_user(email, password, **extra_fields)


# Кастомная модель юзера
class User(AbstractUser):

    username = None
    email = models.EmailField(unique=True, null=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', ]

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.email}'


# Подтверждение логина
class ConfirmLogin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    code = models.IntegerField(null=False)
    access = models.CharField(max_length=200, null=False)
    refresh = models.CharField(max_length=200, null=False)
    date_create = models.DateTimeField(auto_now_add=True, null=False)
    objects = CustomUserManager()

    def __str__(self):
        return f'{self.user}'


# Сессии (сеансы)
class CustomSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    token = models.CharField(max_length=1000, null=False)
    date_create = models.DateTimeField(auto_now_add=True, null=False)

    def __str__(self):
        return f'{self.user}'