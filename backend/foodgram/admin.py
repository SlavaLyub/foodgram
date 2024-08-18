from django.contrib import admin
from .models import User, Subscription, Recipe, Tag, Ingredient, RecipeIngredient, Favorite, ShoppingCart

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'avatar')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscribed_to', 'created_at')
    search_fields = ('user__username', 'subscribed_to__username')
    list_filter = ('created_at',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'cooking_time')
    search_fields = ('title', 'author__username')
    list_filter = ('author', 'tags')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')
    search_fields = ('name',)

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'quantity', 'unit')
    search_fields = ('recipe__title', 'ingredient__name')
    list_filter = ('recipe', 'ingredient')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created_at')
    search_fields = ('user__username', 'recipe__title')
    list_filter = ('created_at',)

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created_at')
    search_fields = ('user__username', 'recipe__title')
    list_filter = ('created_at',)

