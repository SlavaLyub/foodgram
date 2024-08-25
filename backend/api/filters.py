import django_filters
from foodgram.models import Ingredient, Recipe, User


class RecipeFilterSet(django_filters.FilterSet):
    tags = django_filters.CharFilter(method='filter_by_tags')
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

    def filter_by_tags(self, queryset, name, value):
        tag_slugs = self.request.query_params.getlist('tags')
        if tag_slugs:
            return queryset.filter(tags__slug__in=tag_slugs).distinct()
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user and user.is_authenticated:
            is_favorited = value in [True, "1", "true", "True", 1]
            if is_favorited:
                return queryset.filter(favorited_by__user=user).distinct()
            return queryset.exclude(favorited_by__user=user).distinct()
        return queryset.none() if value else queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user and user.is_authenticated:
            is_in_cart = value in [True, "1", "true", "True"]
            if is_in_cart:
                return queryset.filter(shopping_cart_by__user=user).distinct()
            return queryset.exclude(shopping_cart_by__user=user).distinct()
        return queryset.none() if value else queryset


class IngredientFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.rest_framework.CharFilter(field_name='name',
                                                    lookup_expr='startswith'
                                                    )

    class Meta:
        model = Ingredient
        fields = ['name']
