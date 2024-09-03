from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Count

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscription, Tag, User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'avatar')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscribed_to')
    search_fields = ('user__username', 'subscribed_to__username')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1  # Количество пустых форм для добавления новых ингредиентов
    min_num = 1  # Минимальное количество ингредиентов
    max_num = 10  # Максимальное количество ингредиентов
    verbose_name = "Ингредиент"
    verbose_name_plural = "Ингредиенты"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'cooking_time', 'times_favorited')
    search_fields = ('name', 'author__username')
    list_filter = ('tags', 'author')
    raw_id_fields = ('author',)
    filter_horizontal = ('tags',)
    inlines = [RecipeIngredientInline]

    def save_model(self, request, obj, form, change):
        if not obj.ingredients.exists():
            raise ValidationError('Нельзя сохранить рецепт без ингредиентов.')
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(_times_favorited=Count('favorited_by'))
        return qs

    def times_favorited(self, obj):
        return obj._times_favorited
    times_favorited.short_description = 'Times Favorited'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'unit')
    search_fields = ('name',)


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user')
    search_fields = ('recipe__name', 'user__username')
    raw_id_fields = ('recipe', 'user')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user')
    search_fields = ('recipe__name', 'user__username')
    raw_id_fields = ('recipe', 'user')
