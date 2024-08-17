from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import serializers
from base64 import b64decode
from io import BytesIO
from PIL import Image
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer

User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password', 'first_name', 'avatar')


class UserSerializer(serializers.ModelSerializer):
    """Для получения списка пользователей."""
    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name', 'avatar',] # TODO: Добавить в модель поле 'is_subscribed', решить вопрос с получением аватара


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = serializers.CharField()

    class Meta:
        model = User
        fields = ['avatar']

    def validate_avatar(self, value):
        try:
            format, img_str = value.split(';base64,')
            if format not in ['image/png', 'image/jpeg']:
                raise serializers.ValidationError("Ожидалась картинка в формате PNG или JPEG.")
        except ValueError:
            raise serializers.ValidationError("Invalid image format. Ensure the base64 string is correctly formatted.")
        return value

    def update(self, instance, validated_data):
        avatar_data = validated_data['avatar']

        # Decode the base64 string
        format, img_str = avatar_data.split(';base64,')
        img_data = b64decode(img_str)
        image = Image.open(BytesIO(img_data))

        # Save the image
        file_name = f"{instance.username}_avatar.{image.format.lower()}"
        file_path = default_storage.save(file_name, ContentFile(img_data))
        instance.avatar = file_path
        instance.save()

        return instance
