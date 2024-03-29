from django.urls import path
from mainapp.views import *
from django.urls import include


app_name = 'mainapp'

urlpatterns = [
    path('auth/jwt/create/', CustomTokenCreateView.as_view(), name="token_create"),
    path('auth/jwt/refresh/', CustomTokenRefreshView.as_view()),
    path('auth/', include('djoser.urls'), name='register'),
    path('auth/me/', GetMeView.as_view(), name='get_me'),
    path('auth/logout/', LogoutView.as_view()),
    path('auth/logout/all/', LogoutAllView.as_view()),
    path('auth/confirm_login/', ConfirmLoginView.as_view()),
    path('auth/get_sessions/', GetSessionsView.as_view()),
    path('books_list/', GetBooksListView.as_view()),
    path('book/<int:pk>/', ReadBookView.as_view()),
    path('book_create/', CreateBookView.as_view()),
    path('book_change/<int:pk>/', ChangeBookView.as_view()),
    path('role/', RoleView.as_view()),
    path('role/<int:pk>/', ChangeRoleView.as_view()),
    path('role_users/', RoleUserView.as_view()),
    path('permission/', PermissionView.as_view()),
    path('permission/<int:pk>/', ChangePermissionView.as_view()),
]