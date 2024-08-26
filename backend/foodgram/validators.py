import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_name_last_name(value):
    invalid_chars = re.findall(settings.PATTERN_NAME, value)
    if invalid_chars:
        invalid_chars_str = ''.join(invalid_chars)
        raise ValidationError(
            _('The field contains invalid characters: %(invalid_chars)s. '
              'Only letters, spaces, and hyphens are allowed.'),
            params={'invalid_chars': invalid_chars_str},
        )