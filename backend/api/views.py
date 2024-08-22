from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
    ListAPIView,
    # ListCreateAPIView,
    ValidationError
)
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import Http404
# from .filters import RecipeFilter
from .serializers import (
    AvatarSerializer,
    SubscriptionSerializer,
    RecipeListOrRetrieveSerializer,
    RecipePostOrPatchSerializer,
    SubscribeSerializer,
    RecipeLinkSerializer,
    GetOrRetriveIngredientSerializer,
    TagSerializer,
    FavoriteSerializer
)
from foodgram.models import Subscription, Recipe, ShortenedRecipeURL, Ingredient, Tag, FavoriteRecipe
from django import urls
from django.shortcuts import redirect
User = get_user_model()


class UserAvatarUpdateView(RetrieveUpdateDestroyAPIView):
    serializer_class = AvatarSerializer

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Avatar updated'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsListView(ListAPIView):
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        user = self.request.user
        subscriptions = Subscription.objects.filter(user=user)
        subscribed_users = User.objects.filter(id__in=subscriptions.values('subscribed_to'))
        return subscribed_users if subscriptions.exists() else User.objects.none()


class SubscribeCreateDestroyView(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = SubscribeSerializer

    def get_object(self):
        pk = self.kwargs.get('pk')
        subscribed_to = get_object_or_404(User, pk=pk)

        if self.request.user == subscribed_to:
            raise PermissionDenied("You cannot perform actions on your own account.")
        return get_object_or_404(Subscription, user=self.request.user, subscribed_to=subscribed_to)

    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        subscribed_to = get_object_or_404(User, pk=pk)
        if self.request.user == subscribed_to:
            raise ValidationError("You cannot subscribe to yourself.")

        if Subscription.objects.filter(user=self.request.user, subscribed_to=subscribed_to).exists():
            raise ValidationError("You are already subscribed to this user.")

        serializer.save(user=self.request.user, subscribed_to=subscribed_to)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={})  # Empty data since `subscribed_to` is set internally
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            subscribed_to_user = serializer.instance.subscribed_to
            user_detail_serializer = SubscriptionSerializer(subscribed_to_user, context={'request': request})
            data = user_detail_serializer.data

            return Response(data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Http404 as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeListOrRetrieveSerializer

    # В зависимости от действия (list или retrieve) используем разные сериализаторы
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListOrRetrieveSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RecipePostOrPatchSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        'author', 'tags',
        # 'is_favorited', 'is_in_shopping_cart'
    ]


class RecipeLinkView(APIView):
    def get(self, request, id):
        try:
            recipe = Recipe.objects.get(pk=id)
            if not hasattr(recipe, 'shortened_url'):
                ShortenedRecipeURL.objects.create(recipe=recipe)
            serializer = RecipeLinkSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return Response({"detail": "Recipe not found."}, status=status.HTTP_404_NOT_FOUND)


def redirect_to_original(request, short_code):
    url = get_object_or_404(ShortenedRecipeURL, short_code=short_code)
    return redirect(urls.reverse('api:recipe-detail', kwargs={'pk': url.recipe.id}))


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = GetOrRetriveIngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class FavoriteView(ModelViewSet):
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteSerializer
    http_method_names = ['post', 'delete']

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('id')  # Get recipe_id from URL
        recipe = get_object_or_404(Recipe, id=recipe_id)  # Retrieve the Recipe instance

        data = {'user': request.user.id, 'recipe': recipe.id}

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('id')  # Get recipe_id from URL
        recipe = get_object_or_404(Recipe, id=recipe_id)  # Retrieve the Recipe instance

        try:
            favorite_recipe = FavoriteRecipe.objects.get(recipe=recipe, user=self.request.user)
            favorite_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FavoriteRecipe.DoesNotExist:
            return Response({"detail": "This recipe is not in your favorites."}, status=status.HTTP_404_NOT_FOUND)
