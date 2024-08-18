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


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=settings.MAX_LENGTH_TITLE)
    image = models.ImageField(upload_to='recipes/images/')
    description = models.TextField()
    cooking_time = models.PositiveIntegerField()  # Время приготовления в минутах
    tags = models.ManyToManyField('Tag', related_name='recipes')  # Связь многие-ко-многим с Tag

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=settings.MAX_LENGTH_IAG, unique=True)
    slug = models.SlugField(max_length=settings.MAX_LENGTH_IAG, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=settings.MAX_LENGTH_TITLE, unique=True)
    unit = models.CharField(max_length=settings.MAX_LENGTH_UNIT)  # Единица измерения (например, "grams", "cups")

    class Meta:
        verbose_name = "Ingredient"
        verbose_name_plural = "Ingredients"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)

    class Meta:
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f'{self.quantity} {self.unit} of {self.ingredient.name} in {self.recipe.title}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.username} favorited {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='in_shopping_cart')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.username} added {self.recipe.name} to shopping cart'
