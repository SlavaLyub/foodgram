from django.contrib.auth import get_user_model
from django.urls import include, path
from rest_framework.generics import RetrieveAPIView
from rest_framework.routers import DefaultRouter

from .serializers import UserSerializer
from .views import (DownloadShoppingCartView, FavoriteView, IngredientViewSet,
                    RecipeLinkView, RecipeViewSet, ShoppingCartView,
                    SubscribeCreateDestroyView, SubscriptionsListView,
                    TagViewSet, UserAvatarUpdateView)
from .permission import ReadOnly

User = get_user_model()

app_name = 'api'

ACTION = {
    'post': 'create',
    'delete': 'destroy'
}
router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = [
    path('recipes/<int:id>/favorite/',
         FavoriteView.as_view(ACTION),
         name='favorite'),
    path('recipes/download_shopping_cart/',
         DownloadShoppingCartView.as_view(),
         name='download-shopping-cart'),
    path('recipes/<int:id>/shopping_cart/',
         ShoppingCartView.as_view(ACTION),
         name='shopping_cart'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('users/<int:pk>/',
         RetrieveAPIView.as_view(queryset=User.objects.all(),
                                 serializer_class=UserSerializer,
                                 permission_classes=[ReadOnly]),
         name='user_detail'),
    path('users/subscriptions/',
         SubscriptionsListView.as_view(),
         name='subscriptions'),
    path('users/<int:pk>/subscribe/',
         SubscribeCreateDestroyView.as_view(ACTION),
         name='subscribe'),
    path('', include('djoser.urls')),
    path('recipes/<int:id>/get-link/',
         RecipeLinkView.as_view(),
         name='get-recipe-link'),
    path('users/me/avatar/',
         UserAvatarUpdateView.as_view(),
         name='user_avatar_update'),
]
