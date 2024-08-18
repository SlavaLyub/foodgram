from django.contrib.auth.models import AbstractUser
from django.db import models
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

    def __str__(self):  # TODO Добавить сортировку
        return self.username
