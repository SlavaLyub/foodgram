from django.urls import path, include
from .views import UserAvatarUpdateView
urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('users/me/avatar/', UserAvatarUpdateView.as_view(), name='user_avatar_update'),
]
