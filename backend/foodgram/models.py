import random
import string

from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, UniqueConstraint, CheckConstraint

from .validators import validate_name_last_name


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(unique=True,
                              max_length=settings.MAX_LENGTH_EMAIL,
                              verbose_name='Email'
                              )
    username = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                                unique=True,
                                verbose_name='Username',
                                validators=[username_validator],
                                error_messages={
                                    'unique':
                                        "A user with that username already exists.",
                                },
                                )
    first_name = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                                  verbose_name='First Name',
                                  validators=[validate_name_last_name]
                                  )
    last_name = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                                 verbose_name='Last Name',
                                 validators=[validate_name_last_name]
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
        constraints = [
            UniqueConstraint(
                fields=['user', 'subscribed_to'],
                name='unique_subscription'
            ),
            CheckConstraint(
                check=~Q(user=models.F('subscribed_to')),
                name='prevent_self_subscription'
            )
        ]

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

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['name', 'unit'],
                name='unique_ingredients'
            ),
        ]

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
                                   related_name='recipe_ingredients+'
                                   )
    amount = models.PositiveSmallIntegerField()

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
