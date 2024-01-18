from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
User = get_user_model()


# Тестирование создания юзера (регистрации)
class TestRegister(APITestCase):
    def setUp(self):
        self.url = "/api/v1/auth/users/"

    def test_register(self):
        data = {"email": "user1@mail.ru", "password": "Qwerty123!"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# Тестирование получения информации о себе
class TestGetMe(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user1@mail.ru", password="Qwerty123!")
        self.client = APIClient()
        self.url = reverse('mainapp:get_me')

    def test_get_me(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.data['user']['email'], "user1@mail.ru")
