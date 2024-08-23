import django_filters
from foodgram.models import Ingredient, Recipe, Tag, User


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter(field_name="author")
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name="tags", queryset=Tag.objects.all()
    )
    is_favorited = django_filters.BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = django_filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ["author", "tags", "is_favorited", "is_in_shopping_cart"]

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if value:
                return queryset.filter(favorited_by__user=self.request.user)
            return queryset.exclude(favorited_by__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if value:
                return queryset.filter(in_shopping_cart__user=self.request.user)
            return queryset.exclude(in_shopping_cart__user=self.request.user)
        return queryset


class RecipeFilterSet(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        conjoined=False,
        lookup_expr='in'
    )
    author = django_filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_favorited = django_filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value is True:  # Приведение значения к булевому типу
                return queryset.filter(favorited_by__user=user).distinct()
            elif value is False:
                return queryset.exclude(favorited_by__user=user).distinct()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, value):
        user = self.request.user
        if user.is_authenticated:
            if value is True:
                return queryset.filter(shopping_cart_by__user=user).distinct()
            return queryset.exclude(shopping_cart_by__user=user).distinct()
        return queryset


class IngredientFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.rest_framework.CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']

