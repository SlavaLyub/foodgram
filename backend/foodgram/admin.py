from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count
from django.forms.models import BaseInlineFormSet
from django.utils.html import format_html

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


class RecipeIngredientInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        if not any(
                form.cleaned_data for form in self.forms
                if form.cleaned_data and not form.cleaned_data.get(
                    'DELETE', False
                )):
            raise ValidationError(
                "A recipe must have at least one ingredient."
            )


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    formset = RecipeIngredientInlineFormSet
    extra = 1
    min_num = 1
    validate_min = True


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author',
                    'cooking_time', 'times_favorited',
                    'image_tag'
                    )
    search_fields = ('name', 'author__username')
    list_filter = ('tags', 'author')
    raw_id_fields = ('author',)
    filter_horizontal = ('tags',)
    inlines = [RecipeIngredientInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(_times_favorited=Count('favorited_by'))
        return qs

    def times_favorited(self, obj):
        return obj._times_favorited

    times_favorited.short_description = 'Times Favorited'

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />',
                               obj.image.url)
        return '-'

    image_tag.short_description = 'Image'

    @transaction.atomic
    def save_formset(self, request, form, formset, change):
        if isinstance(formset, RecipeIngredientInlineFormSet):
            formset.clean()
            formset.instance = form.instance
            formset.save()

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        inline_instances = self.get_inline_instances(request)
        for inline in inline_instances:
            formset = inline.get_formset(request, obj=obj)
            if isinstance(formset, RecipeIngredientInlineFormSet):
                formset.instance = obj
                formset.clean()
                formset.save()


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
