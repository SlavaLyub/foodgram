from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from base64 import b64decode
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from foodgram.models import Recipe, Tag, Ingredient, RecipeIngredient, Subscription

User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'password',
            'first_name',
            'avatar'
        )


class UserSerializer(serializers.ModelSerializer):
    """Для получения списка пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, subscribed_to=obj).exists()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')
            # И извлечь расширение файла.
            ext = format.split('/')[-1]
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
            data = ContentFile(b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class SubscriptionSerializer(serializers.ModelSerializer):
    """Для получения списка пользователей."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, subscribed_to=obj).exists()

    def get_recipes(self, obj):
        return []

    def get_recipes_count(self, obj):
        return len(self.get_recipes(obj))


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['user', 'subscribed_to', 'created_at']
        read_only_fields = ['user', 'subscribed_to', 'created_at']


################################################################

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ingredient.name')
    unit = serializers.CharField(source='ingredient.unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'unit', 'amount']


class RecipeListOrRetrieveSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time']

################################################################


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    # amount = serializers.DecimalField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipePostOrPatchSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = IngredientCreateSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = [
            'tags', 'ingredients', 'author',
            'name', 'image', 'text', 'cooking_time'
        ]

    def create(self, validated_data):
        # Извлечение данных ингредиентов
        ingredients_data = validated_data.pop('ingredients')

        # Создание рецепта
        # recipe = Recipe.objects.create(**validated_data)
        recipe = super().create(validated_data)

        # Создание связей с ингредиентами
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data.pop('id')  # Получение объекта ингредиента
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                # amount=ingredient_data['amount']
                **ingredient_data  # Присвоение остальных полей
            )
        recipe.refresh_from_db()
        return recipe

################################################################
