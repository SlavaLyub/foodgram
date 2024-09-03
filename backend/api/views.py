from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import (RetrieveUpdateDestroyAPIView,
                                     ValidationError, get_object_or_404)
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from foodgram.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                             Subscription, Tag)

from .filters import RecipeFilterSet
from .pagination import LimitPagination
from .permission import IsAuthenticatedOrAuthorOrReadOnly
from .serializers import (AvatarSerializer, FavoriteSerializer,
                          GetOrRetriveIngredientSerializer,
                          RecipeLinkSerializer, RecipeListOrRetrieveSerializer,
                          RecipePostOrPatchSerializer, ShoppingCartSerializer,
                          SubList, SubscriptionSerializer, TagSerializer)

User = get_user_model()


class BaseRecipeFavorAndShoppingView(CreateModelMixin,
                                     DestroyModelMixin,
                                     GenericViewSet):
    model = None
    serializer_class = None
    error_message = "Рецепт не добавлен."

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)

        serializer = self.get_serializer(
            data={'user': request.user.id, 'recipe': recipe.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, recipe=recipe)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)

        instance = self.model.objects.filter(user=request.user,
                                             recipe=recipe).first()
        if instance:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"detail": self.error_message},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserAvatarUpdateView(RetrieveUpdateDestroyAPIView):
    serializer_class = AvatarSerializer

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user,
                                         data=request.data,
                                         partial=True
                                         )
        serializer.is_valid(raise_exceptions=True)
        serializer.save()
        return Response({'status': 'Avatar updated'},
                        status=status.HTTP_200_OK
                        )

    def delete(self, request, *args, **kwargs):
        try:
            user: User = self.request.user
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionViewSet(viewsets.GenericViewSet, ListModelMixin):
    pagination_class = LimitPagination

    def get_queryset(self):
        user = self.request.user
        return Subscription.objects.filter(user=user)

    @action(detail=False,
            methods=['get'],
            url_path='subscriptions',
            url_name='subscriptions'
            )
    def list_subscriptions(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubList(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = SubList(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True,
            methods=['post'],
            url_path='subscribe',
            url_name='subscribe'
            )
    def subscribe(self, request, pk=None):
        subscribed_to = get_object_or_404(User, pk=pk)
        serializer = SubscriptionSerializer(
            data={"subscribed_to": subscribed_to.id, "user": request.user.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"errors": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        user = request.user
        subscribed_to = get_object_or_404(User, pk=pk)
        subscription = Subscription.objects.filter(user=user,
                                                   subscribed_to=subscribed_to
                                                   ).first()
        if not subscription:
            return Response({'error': 'Subscription does not exist.'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeLinkView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        try:
            recipe = Recipe.objects.get(pk=id)
            if not recipe.short_url:
                recipe.short_url = recipe.generate_short_url()
                recipe.save(update_fields=['short_url'])
            serializer = RecipeLinkSerializer(recipe,
                                              context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return Response(
                {"detail": "Recipe not found."},
                status=status.HTTP_404_NOT_FOUND
            )


def redirect_to_original(request, short_code):
    recipe = get_object_or_404(Recipe, short_url=short_code)
    return redirect('recipe-detail', id=recipe.id)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = GetOrRetriveIngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']
    pagination_class = None
    permission_classes = [permissions.AllowAny]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [permissions.AllowAny]


class FavoriteView(BaseRecipeFavorAndShoppingView):
    model = FavoriteRecipe
    serializer_class = FavoriteSerializer


class ShoppingCartView(BaseRecipeFavorAndShoppingView):
    model = ShoppingCart
    serializer_class = ShoppingCartSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = RecipeFilterSet
    pagination_class = LimitPagination
    permission_classes = [IsAuthenticatedOrAuthorOrReadOnly, ]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListOrRetrieveSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RecipePostOrPatchSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request, *args, **kwargs):
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
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_cart.txt"'
        return response
