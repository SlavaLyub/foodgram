# import django_filters
# from foodgram.models import Recipe, Tag, Favorite, ShoppingCart
#
# class RecipeFilter(django_filters.FilterSet):
#     author = django_filters.NumberFilter(field_name='author')
#     tags = django_filters.ModelMultipleChoiceFilter(
#         field_name='tags',
#         queryset=Tag.objects.all()
#     )
#     is_favorited = django_filters.BooleanFilter(method='filter_is_favorited')
#     is_in_shopping_cart = django_filters.BooleanFilter(method='filter_is_in_shopping_cart')
#
#     class Meta:
#         model = Recipe
#         fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
#
#     def filter_is_favorited(self, queryset, name, value):
#         if self.request.user.is_authenticated:
#             if value:
#                 return queryset.filter(favorited_by__user=self.request.user)
#             return queryset.exclude(favorited_by__user=self.request.user)
#         return queryset
#
#     def filter_is_in_shopping_cart(self, queryset, name, value):
#         if self.request.user.is_authenticated:
#             if value:
#                 return queryset.filter(in_shopping_cart__user=self.request.user)
#             return queryset.exclude(in_shopping_cart__user=self.request.user)
#         return queryset
