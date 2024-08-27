import django_filters
from foodgram.models import Ingredient, Recipe, User, Tag, FavoriteRecipe


class RecipeFilterSet(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        label='Теги'
    )
    author = django_filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_favorited = django_filters.CharFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user and user.is_authenticated and value:
            return queryset.filter(favorited_by__user=user).distinct()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user and user.is_authenticated and value:
            return queryset.filter(shopping_cart_by__user=user).distinct()
        return queryset


class IngredientFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.rest_framework.CharFilter(field_name='name',
                                                    lookup_expr='startswith'
                                                    )

    class Meta:
        model = Ingredient
        fields = ['name']
