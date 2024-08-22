import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_username(username):
    if not re.match(settings.PATTERN_NAME, username):
        raise ValidationError(
            _('Используются недопустимые символы в имени пользователя.'),
            params={'value': username},
        )
