import random
import string

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, UniqueConstraint, CheckConstraint

from .validators import validate_name_last_name
from .constants import constants


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(
        unique=True,
        max_length=constants['MAX_LENGTH_NAME'],
        verbose_name='Электронная почта',
        help_text='Введите свой адрес электронной почты.'
    )
    username = models.CharField(
        max_length=constants['MAX_LENGTH_NAME'],
        unique=True,
        verbose_name='Имя пользователя',
        validators=[username_validator],
        error_messages={
            'unique': "Пользователь с таким именем уже существует.",
        },
        help_text='Введите уникальное имя пользователя.'
    )
    first_name = models.CharField(
        max_length=constants['MAX_LENGTH_NAME'],
        verbose_name='Имя',
        validators=[validate_name_last_name],
        help_text='Введите ваше имя.'
    )
    last_name = models.CharField(
        max_length=constants['MAX_LENGTH_NAME'],
        verbose_name='Фамилия',
        validators=[validate_name_last_name],
        help_text='Введите вашу фамилию.'
    )
    avatar = models.ImageField(
        upload_to='users/avatars',
        verbose_name='Фото профиля',
        null=True,
        default=None,
        help_text='Загрузите фото профиля.'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
        help_text='Пользователь, который подписывается.'
    )
    subscribed_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='На кого подписан',
        help_text='Пользователь, на которого подписываются.'
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
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.subscribed_to}'


class Tag(models.Model):
    name = models.CharField(
        max_length=constants['MAX_LENGTH_UNIT'],
        unique=True,
        verbose_name='Название тега',
        help_text='Введите название тега.'
    )
    slug = models.SlugField(
        max_length=constants['MAX_LENGTH_UNIT'],
        unique=True,
        verbose_name='Слаг',
        help_text='Слаг тега, используется в URL.'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=constants['MAX_LENGTH_TAG'],
        unique=True,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента.'
    )
    unit = models.CharField(
        max_length=constants['MAX_LENGTH_UNIT'],
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения для ингредиента.'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['name', 'unit'],
                name='unique_ingredients'
            ),
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


def generate_short_code():
    characters = string.ascii_letters + string.digits

    while True:
        short_code = ''.join(random.choices(characters,
                                            k=constants['MAX_LENGTH_SHORT_URL']
                                            ))
        if not Recipe.objects.filter(short_url=short_code).exists():
            return short_code


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Автор рецепта.'
    )
    name = models.CharField(
        max_length=constants['MAX_LENGTH_TAG'],
        verbose_name='Название рецепта',
        help_text='Введите название рецепта.'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение рецепта',
        help_text='Загрузите изображение для рецепта.'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите полное описание рецепта.'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        help_text='Введите время приготовления в минутах.'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        help_text='Выберите теги для рецепта.'
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        help_text='Дата и время создания рецепта.'
    )
    short_url = models.CharField(
        max_length=constants['MAX_LENGTH_SHORT_URL'],
        unique=True,
        default=generate_short_code,
        verbose_name='Короткий URL',
        help_text='Короткий URL для рецепта.'
    )

    class Meta:
        unique_together = ('author', 'name')
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-date_created']

    def __str__(self):
        return self.name

    def clean(self):
        if Recipe.objects.filter(
                short_url=self.short_url).exclude(pk=self.pk).exists():
            raise ValidationError(
                "URL уже используется. Пожалуйста, сгенерируйте новый."
            )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепт',
        help_text='Рецепт, к которому относится этот ингредиент.'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
        help_text='Ингредиент, используемый в рецепте.'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Введите количество ингредиента, используемого в рецепте.'
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return (
            f'{self.amount} {self.ingredient.unit} '
            f'{self.ingredient.name} в {self.recipe.name}'
        )


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Пользователь',
        help_text='Пользователь, добавивший этот рецепт в избранное.'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Рецепт',
        help_text='Рецепт, который был добавлен в избранное.'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
        help_text='Дата и время, когда рецепт был добавлен в избранное.'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipes'
            ),
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipes',
        verbose_name='Пользователь',
        help_text='Пользователь, добавивший этот рецепт в корзину покупок.'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart_by',
        verbose_name='Рецепт',
        help_text='Рецепт, который был добавлен в корзину покупок.'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
        help_text='Дата и время, когда рецепт был добавлен в корзину покупок.'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            ),
        ]
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name}'
