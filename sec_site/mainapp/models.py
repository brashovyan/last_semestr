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

        user = self._create_user(email, password, **extra_fields)

        # Создаю дефолтные разрешения, если их нет
        read_all = CustomPermission.objects.filter(title="read_all")
        if not read_all:
            CustomPermission.objects.create(title="read_all")
        read_access = CustomPermission.objects.filter(title="read_access")
        if not read_access:
            CustomPermission.objects.create(title="read_access")
        create_all = CustomPermission.objects.filter(title="create_all")
        if not create_all:
            CustomPermission.objects.create(title="create_all")
        create_access = CustomPermission.objects.filter(title="create_access")
        if not create_access:
            CustomPermission.objects.create(title="create_access")
        put_all = CustomPermission.objects.filter(title="put_all")
        if not put_all:
            CustomPermission.objects.create(title="put_all")
        put_access = CustomPermission.objects.filter(title="put_access")
        if not put_access:
            CustomPermission.objects.create(title="put_access")
        delete_all = CustomPermission.objects.filter(title="delete_all")
        if not delete_all:
            CustomPermission.objects.create(title="delete_all")
        delete_access = CustomPermission.objects.filter(title="delete_access")
        if not delete_access:
            CustomPermission.objects.create(title="delete_access")

        # Создаю роль Админа, если ёё нет
        admin = CustomRole.objects.filter(title="admin")
        if not admin:
            r_all = CustomPermission.objects.get(title='read_all')
            c_all = CustomPermission.objects.get(title='create_all')
            p_all = CustomPermission.objects.get(title='put_all')
            d_all = CustomPermission.objects.get(title='delete_all')
            role = CustomRole.objects.create(title="admin")
            role.users.add(user)
            role.permissions.add(r_all, c_all, p_all, d_all)

        # Создаю роль обычного юзера
        usual_reader = CustomRole.objects.filter(title="usual_reader")
        if not usual_reader:
            r_access = CustomPermission.objects.get(title='read_access')
            role = CustomRole.objects.create(title="usual_reader")
            role.users.add(user)
            role.permissions.add(r_access)

        return user


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
    objects = CustomUserManager()

    def __str__(self):
        return f'{self.user}'


class CustomPermission(models.Model):
    title = models.CharField(max_length=1000, null=False, unique=True)
    objects = CustomUserManager()

    def __str__(self):
        return f'{self.title}'


class CustomRole(models.Model):
    title = models.CharField(max_length=1000, null=False, unique=True)
    permissions = models.ManyToManyField(CustomPermission, related_name="permissions")
    users = models.ManyToManyField(User, related_name="roles")
    objects = CustomUserManager()

    def __str__(self):
        return f'{self.title}'


class Book(models.Model):
    title = models.CharField(max_length=1000, null=False)
    description = models.CharField(max_length=3000, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    authors = models.ManyToManyField(User, related_name="books")
    objects = CustomUserManager()

    def __str__(self):
        return f'{self.title}'
