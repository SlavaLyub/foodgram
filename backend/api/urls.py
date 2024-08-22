from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework.generics import RetrieveAPIView
from .views import (
    UserAvatarUpdateView,
    SubscriptionsListView,
    RecipeViewSet,
    RecipeLinkView,
    SubscribeCreateDestroyView,
    IngredientViewSet,
    TagViewSet,
    FavoriteView,
)
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

app_name = 'api'

SUBSCRIBE = {
    'post': 'create',
    'delete': 'destroy'
}
router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'tags', TagViewSet, basename='tag')
# router.register(r'recipes/(?P<id>\d+)/favorite', FavoriteView, basename='favorite')

urlpatterns = [
    path('recipes/<int:id>/favorite/', FavoriteView.as_view(SUBSCRIBE), name='favorite'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('users/<int:pk>/', RetrieveAPIView.as_view(queryset=User.objects.all(), serializer_class=UserSerializer), name='user_detail'),
    path('users/subscriptions/', SubscriptionsListView.as_view(), name='subscriptions'),
    path('users/<int:pk>/subscribe/', SubscribeCreateDestroyView.as_view(SUBSCRIBE), name='subscribe'),
    path('', include('djoser.urls')),
    path('recipes/<int:id>/get-link/', RecipeLinkView.as_view(), name='get-recipe-link'),
    path('users/me/avatar/', UserAvatarUpdateView.as_view(), name='user_avatar_update'),

]
