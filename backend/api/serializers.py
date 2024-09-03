from base64 import b64decode

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from foodgram.models import (FavoriteRecipe, Ingredient, Recipe,
                             RecipeIngredient, ShoppingCart, Subscription, Tag)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Для получения списка пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'avatar', 'is_subscribed'
                  ]

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user,
                                           subscribed_to=obj).exists()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class SubList(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="subscribed_to.id")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    username = serializers.ReadOnlyField(source="subscribed_to.username")
    first_name = serializers.ReadOnlyField(source="subscribed_to.first_name")
    last_name = serializers.ReadOnlyField(source="subscribed_to.last_name")
    avatar = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField(source="subscribed_to.email")

    class Meta:
        model = Subscription
        fields = [
            "email", "id", "username", "first_name", "last_name",
            "is_subscribed", "recipes", "recipes_count", "avatar",
        ]

    def get_avatar(self, obj):
        return (
            obj.subscribed_to.avatar.url if obj.subscribed_to.avatar else None
        )

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        return (
            not user.is_anonymous
            and Subscription.objects.filter(
                user=user,
                subscribed_to=obj.subscribed_to).exists())

    def get_recipes(self, obj):
        recipes = obj.subscribed_to.recipes.all()
        recipes_limit = (
            self.context['request'].query_params.get("recipes_limit")
        )
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return [
            {
                "id": recipe.id,
                "name": recipe.name,
                "image": recipe.image.url,
                "cooking_time": recipe.cooking_time,
            }
            for recipe in recipes
        ]

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.subscribed_to).count()


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    username = serializers.ReadOnlyField(source="subscribed_to.username")
    first_name = serializers.ReadOnlyField(source="subscribed_to.first_name")
    last_name = serializers.ReadOnlyField(source="subscribed_to.last_name")
    avatar = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField(source="subscribed_to.email")
    subscribed_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )

    class Meta:
        model = Subscription
        fields = [
            "email", "id", "username", "first_name", "last_name",
            "is_subscribed", "recipes", "recipes_count",
            "subscribed_to", "avatar",
        ]

    def validate(self, data):
        user = self.context["request"].user
        subscribed_to = data['subscribed_to']
        if user == subscribed_to:
            raise serializers.ValidationError(
                {"subscription": "You can't subscribe to yourself."}
            )
        if Subscription.objects.filter(user=user,
                                       subscribed_to=subscribed_to).exists():
            raise serializers.ValidationError(
                {"subscription": "You are already subscribed to this user."}
            )
        data['user'] = user
        return data

    def get_avatar(self, obj):
        if obj.subscribed_to.avatar:
            return obj.subscribed_to.avatar.url
        return None

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user,
                                           subscribed_to=obj.subscribed_to
                                           ).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.subscribed_to)
        return [
            {
                "id": recipe.id,
                "name": recipe.name,
                "image": recipe.image.url,
                "cooking_time": recipe.cooking_time,
            }
            for recipe in recipes
        ]

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.subscribed_to).count()

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["id"] = instance.subscribed_to.id
        recipes_limit = (
            self.context['request'].query_params.get("recipes_limit")
        )
        if recipes_limit:
            repr['recipes'] = repr['recipes'][:int(recipes_limit)]
        return repr

    def create(self, validated_data):
        return Subscription.objects.create(**validated_data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class GetOrRetriveIngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField(source="unit")

    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class RecipeListOrRetrieveSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time']

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return FavoriteRecipe.objects.filter(user=user,
                                                 recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_ingredients(self, obj):
        return [
            {
                "id": ingredient.ingredient.id,
                "name": ingredient.ingredient.name,
                "measurement_unit": ingredient.ingredient.unit,
                "amount": ingredient.amount,
            }
            for ingredient in obj.ingredients.all()
        ]


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipePostOrPatchSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = IngredientCreateSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'ingredients', 'tags', 'author',
            'image', 'name', 'text', 'cooking_time'
        ]

    def validate_image(self, image):
        if self.context.get("request").method == "POST" and not image:
            raise serializers.ValidationError('Image must be required')
        return image

    def validate(self, data):
        ingredient = set()
        tags = set()
        if not data.get('tags'):
            raise ValidationError(
                {"tags": "Recipe should have at least one tag."}
            )
        for item in data.get('tags'):
            tags.add(item)
        if len(tags) != len(data.get('tags')):
            raise ValidationError({"tags": "unique constraint failed."})

        if not data.get('ingredients'):
            raise ValidationError(
                {"ingredients": "Recipe should have at least one ingredient."}
            )
        for item in data.get('ingredients'):
            ingredient.add(item['id'])
            if item['amount'] < 1:
                raise ValidationError(
                    {
                        "ingredients":
                            "Amount value should be greater than 1 or equal."
                    }
                )
        if len(ingredient) != len(data.get('ingredients')):
            raise ValidationError({"ingredients": "unique constraint failed."})
        if data.get('cooking_time') < 1:
            raise ValidationError(
                {
                    "ingredients":
                        "Amount value should be greater than 1 or equal."
                }
            )
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = super().create(validated_data)
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data.pop("id")
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                **ingredient_data,
            )
        recipe.refresh_from_db()
        return recipe

    def update(self, instance, validated_data):
        if validated_data.get("ingredients"):
            ingredients_data = validated_data.pop("ingredients")

            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data.pop("id")
                recipe_ingredient, _ = (
                    RecipeIngredient.objects.update_or_create(
                        recipe=instance,
                        ingredient_id=ingredient_id,
                        defaults=ingredient_data,
                    ))
        super().update(instance, validated_data)

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        current_user = request.user

        representation['id'] = instance.id

        # Проверка подписки
        is_subscribed = Subscription.objects.filter(
            user=current_user,
            subscribed_to=instance.author).exists()
        representation['author'] = {
            "email": instance.author.email,
            "id": instance.author.id,
            "username": instance.author.username,
            "first_name": instance.author.first_name,
            "last_name": instance.author.last_name,
            "is_subscribed": is_subscribed,
            "avatar": (
                instance.author.avatar.url
                if instance.author.avatar
                else None
            )}

        representation['tags'] = [
            {
                "id": tag.id,
                "name": tag.name,
                "slug": tag.slug
            } for tag in instance.tags.all()
        ]

        representation['ingredients'] = [
            {
                "id": ingredient.ingredient.id,
                "name": ingredient.ingredient.name,
                "measurement_unit": ingredient.ingredient.unit,
                "amount": ingredient.amount
            } for ingredient in instance.ingredients.all()
        ]

        representation['image'] = (
            request.build_absolute_uri(instance.image.url)
        )
        representation['is_favorited'] = (
            FavoriteRecipe.objects.filter(
                user=current_user, recipe=instance).exists()
        )
        representation['is_in_shopping_cart'] = (
            ShoppingCart.objects.filter(
                user=current_user, recipe=instance).exists()
        )
        return representation


class RecipeLinkSerializer(serializers.ModelSerializer):
    short_link = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['short_link']

    def get_short_link(self, obj):
        request = self.context.get('request')
        short_code = obj.short_url
        return request.build_absolute_uri(f'/s/{short_code}/')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['short-link'] = representation.pop('short_link')
        return representation


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ['user', 'recipe']

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Recipe already in favorites.')
        return FavoriteRecipe.objects.create(user=user, recipe=recipe)

    def to_representation(self, instance):
        recipe = instance.recipe
        return {
            'id': recipe.id,
            'name': recipe.name,
            'image': recipe.image.url,
            'cooking_time': recipe.cooking_time
        }


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    image = serializers.ReadOnlyField(source='recipe.image.url')
    name = serializers.ReadOnlyField(source='recipe.name')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ['id', 'image', 'name', 'cooking_time']

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Recipe already in shopping cart.'
            )

        return ShoppingCart.objects.create(user=user, recipe=recipe)
