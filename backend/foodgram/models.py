import random
import string

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    email = models.EmailField(unique=True,
                              max_length=settings.MAX_LENGTH_EMAIL,
                              verbose_name='Email'
                              )
    username = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                                unique=True,
                                verbose_name='Username',
                                validators=[validate_username]
                                )
    first_name = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                                  verbose_name='First Name'
                                  )
    last_name = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                                 verbose_name='Last Name'
                                 )
    avatar = models.ImageField(upload_to='users/avatars',
                               verbose_name='Фото профиля',
                               null=True,
                               default=None
                               )

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='subscriptions'
                             )
    subscribed_to = models.ForeignKey(User,
                                      on_delete=models.CASCADE,
                                      related_name='subscribers'
                                      )

    class Meta:
        unique_together = ('user', 'subscribed_to')

    def __str__(self):
        return f'{self.user} subscribed to {self.subscribed_to}'


class Tag(models.Model):
    name = models.CharField(max_length=settings.MAX_LENGTH_UNIT,
                            unique=True
                            )
    slug = models.SlugField(max_length=settings.MAX_LENGTH_UNIT,
                            unique=True
                            )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=settings.MAX_LENGTH_IAG,
                            unique=True
                            )
    unit = models.CharField(max_length=settings.MAX_LENGTH_UNIT)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes'
                               )
    name = models.CharField(max_length=settings.MAX_LENGTH_IAG)
    image = models.ImageField(upload_to='recipes/images/')
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()
    tags = models.ManyToManyField(Tag,
                                  related_name='recipes'
                                  )
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('author', 'name')
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"
        ordering = ['-date_created']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='ingredients'
                               )
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='recipe_ingredients'
                                   )
    amount = models.IntegerField()

    class Meta:
        unique_together = ('recipe', 'ingredient')
        verbose_name = "Recipe Ingredient"
        verbose_name_plural = "Recipe Ingredients"

    def __str__(self):
        return (
            f'{self.amount} {self.ingredient.unit} of '
            f'{self.ingredient.name} in {self.recipe.name}'
        )


def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


class ShortenedRecipeURL(models.Model):
    recipe = models.OneToOneField(Recipe,
                                  on_delete=models.CASCADE,
                                  related_name='shortened_url'
                                  )
    short_code = models.CharField(max_length=settings.MAX_LENGTH_SHORT_URL,
                                  unique=True,
                                  default=generate_short_code
                                  )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.short_code} -> {self.recipe.name}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorite_recipes'
                             )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorited_by'
                               )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shopping_cart_recipes'
                             )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='shopping_cart_by'
                               )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name}'
