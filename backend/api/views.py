from django import urls
from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.urls import reverse
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets, permissions
from rest_framework.generics import (ListAPIView, RetrieveUpdateDestroyAPIView,
                                     ValidationError, get_object_or_404)
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from foodgram.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                             Subscription, Tag, generate_short_code)

from .serializers import (AvatarSerializer, FavoriteSerializer,
                          GetOrRetriveIngredientSerializer,
                          RecipeLinkSerializer, RecipeListOrRetrieveSerializer,
                          RecipePostOrPatchSerializer, ShoppingCartSerializer,
                          SubList, SubscriptionSerializer,
                          TagSerializer)
from .filters import IngredientFilter, RecipeFilterSet
from .pagination import LimitPagination
from .permission import IsAuthorOrReadOnly

User = get_user_model()


class UserAvatarUpdateView(RetrieveUpdateDestroyAPIView):
    serializer_class = AvatarSerializer

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user,
                                         data=request.data,
                                         partial=True
                                         )
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Avatar updated'},
                            status=status.HTTP_200_OK
                            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            user: User = get_object_or_404(User, pk=self.request.user.id)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsListView(ListAPIView):
    serializer_class = SubList
    pagination_class = LimitPagination

    def get_queryset(self):
        user = self.request.user
        subscriptions = Subscription.objects.filter(user=user)
        return (
            subscriptions if
            subscriptions.exists() else
            Subscription.objects.none()
        )


class SubscribeCreateDestroyView(CreateModelMixin, DestroyModelMixin,
                                 GenericViewSet
                                 ):
    serializer_class = SubscriptionSerializer

    def get_object(self):
        pk = self.kwargs.get("pk")
        subscribed_to = get_object_or_404(User, pk=pk)
        return get_object_or_404(
            Subscription, user=self.request.user, subscribed_to=subscribed_to
        )

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        subscribed_to = get_object_or_404(User, pk=pk)
        serializer = self.get_serializer(
            data={"subscribed_to": subscribed_to.id,
                  "user": request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED,
                            headers=headers
                            )
        except ValidationError as e:
            return Response({"errors": str(e)},
                            status=status.HTTP_400_BAD_REQUEST
                            )

    def destroy(self, request, *args, **kwargs):
        user = request.user
        subscribed_to_id = kwargs.get('pk')
        try:
            author = User.objects.get(pk=subscribed_to_id)
        except User.DoesNotExist:
            return Response({'error': 'Author not found.'},
                            status=status.HTTP_404_NOT_FOUND
                            )
        subscription = Subscription.objects.filter(user=user,
                                                   subscribed_to=author
                                                   ).first()
        if not subscription:
            return Response({'error': 'Subscription does not exist.'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = RecipeFilterSet
    filterset_fields = ['author', 'tags',
                        'is_favorited', 'is_in_shopping_cart'
                        ]
    pagination_class = LimitPagination
    permission_classes = [IsAuthorOrReadOnly, ]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListOrRetrieveSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RecipePostOrPatchSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance,
                                         data=request.data, partial=True
                                         )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class RecipeLinkView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        try:
            recipe = Recipe.objects.get(pk=id)
            if not recipe.short_url:  # Если короткий URL не установлен
                recipe.short_url = generate_short_code()
                recipe.save()  # Сохраняем обновлённый рецепт с коротким URL
            serializer = RecipeLinkSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return Response({"detail": "Recipe not found."}, status=status.HTTP_404_NOT_FOUND)


def redirect_to_original(request, short_code):
    # Ищем рецепт по short_url
    recipe = get_object_or_404(Recipe, short_url=short_code)
    # Перенаправляем на детальное представление рецепта
    return redirect(reverse('api:recipe-detail', kwargs={'pk': recipe.id}))


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = GetOrRetriveIngredientSerializer
    filterset_class = IngredientFilter
    pagination_class = None
    permission_classes = [permissions.AllowAny]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [permissions.AllowAny]


class FavoriteView(ModelViewSet):
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteSerializer

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        data = {'user': request.user.id, 'recipe': recipe.id}

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_data = serializer.to_representation(serializer.instance)
        return Response(response_data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        try:
            favorite_recipe = FavoriteRecipe.objects.get(
                recipe=recipe,
                user=self.request.user
            )
            favorite_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FavoriteRecipe.DoesNotExist:
            return Response(
                {"detail": "This recipe is not in your favorites."},
                status=status.HTTP_400_BAD_REQUEST
            )


class ShoppingCartView(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    http_method_names = ['post', 'delete']

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if ShoppingCart.objects.filter(user=request.user,
                                       recipe=recipe
                                       ).exists():
            return Response(
                {'error': 'Recipe already in shopping cart.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data={'user': request.user.id,
                                               'recipe': recipe.id}
                                         )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, recipe=recipe)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers
                        )

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)

        shopping_cart_item = ShoppingCart.objects.filter(
            recipe=recipe, user=request.user
        ).first()
        if shopping_cart_item:
            shopping_cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # Возвращаем статус 400, как ожидается в тестах
            return Response(
                {"detail": "Recipe is not in your shopping cart."},
                status=status.HTTP_400_BAD_REQUEST
            )


class DownloadShoppingCartView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        ingredients = {}
        for item in shopping_cart:
            recipe = item.recipe
            for ingredient in recipe.ingredients.all():
                name = ingredient.ingredient.name
                amount = ingredient.amount
                unit = ingredient.ingredient.unit

                if name in ingredients:
                    ingredients[name]['amount'] += amount
                else:
                    ingredients[name] = {'amount': amount, 'unit': unit}
        content = "Shopping Cart Ingredients:\n\n"
        for name, details in ingredients.items():
            content += f"{name}: {details['amount']} {details['unit']}\n"
        response = FileResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"')
        return response
