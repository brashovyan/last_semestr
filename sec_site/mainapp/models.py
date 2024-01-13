from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager


# Убираю у юзера поле username, и делаю вместо него email. Логин через email
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
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        assert extra_fields['is_staff']
        assert extra_fields['is_superuser']
        return self._create_user(email, password, **extra_fields)


# кастомная модель юзера
class User(AbstractUser):

    username = None
    email = models.EmailField(unique=True, null=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', ]

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.email}'


# Кастомные сессии
class CustomSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    token = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return f'{self.user}'

