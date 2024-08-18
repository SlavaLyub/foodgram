from django.urls import path, include
from .views import UserAvatarUpdateView, SubscriptionsListView, RecipeListView, RecipeDetailView, SubscribeCreateDestroyView

SUBSCRIBE = {
    'post': 'create',
    'delete': 'destroy'
}

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/', RecipeListView.as_view(), name='recipe_list'),
    path('recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe_detail'),
    path('users/subscriptions/', SubscriptionsListView.as_view(), name='subscriptions'),
    path('users/<int:pk>/subscribe/', SubscribeCreateDestroyView.as_view(SUBSCRIBE), name='subscribe'),
    path('', include('djoser.urls')),
    path('users/me/avatar/', UserAvatarUpdateView.as_view(), name='user_avatar_update'),
]
