from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
from .validators import validate_username


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=settings.MAX_LENGTH_EMAIL,
        verbose_name='Email'
    )
    username = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        unique=True,
        verbose_name='Username',
        validators=[validate_username]
    )
    first_name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        verbose_name='First Name'
    )
    avatar = models.ImageField(
        upload_to='users/avatars',
        verbose_name='Фото профиля',
        null=True,
        default=None
    )

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    subscribed_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'subscribed_to')

    def __str__(self):
        return f'{self.user} subscribed to {self.subscribed_to}'


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='recipes/images/')
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()
    tags = models.ManyToManyField(Tag, related_name='recipes')

    class Meta:
        unique_together = ('author', 'name')
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredients')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('recipe', 'ingredient')
        verbose_name = "Recipe Ingredient"
        verbose_name_plural = "Recipe Ingredients"

    def __str__(self):
        return f'{self.amount} {self.ingredient.unit} of {self.ingredient.name} in {self.recipe.name}'
