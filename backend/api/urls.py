from django.urls import path, include
from .views import UserAvatarUpdateView
urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    #  path('users/', UserListView.as_view(), name='user_list'),
    path('', include('djoser.urls')),  # TODO: Если этот эндпоинт выше 5-й строчки, он перехватыват вывод пользователей
    path('users/me/avatar/', UserAvatarUpdateView.as_view(), name='user_avatar_update'),
]
