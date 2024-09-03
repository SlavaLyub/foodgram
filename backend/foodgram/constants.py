import string

# Константы
MAX_LENGTH_NAME = 150
MAX_LENGTH_EMAIL = 254
MAX_LENGTH_PASSWORD = 128
PAGINATION_LIMIT = 10

USERNAME_RESTRICT_PATTERN = r'[\w.@+-]'
NAMES_ALLOW_PATTERN = r'[a-zA-Zа-яА-ЯёЁ\-]'
TAG_ALLOW_PATTERN = r'[a-zA-Zа-яА-ЯёЁ\s\-]'
NAME_RECIPE_PATTERN = r'[a-zA-Zа-яА-ЯёЁ\s\-\(\)]'
ERROR_MESSAGE = 'The field contains invalid characters.'

MAX_LENGTH_TITLE = 255
MAX_LENGTH_TAG = 100
MAX_LENGTH_UNIT = 50
MAX_LENGTH_AMOUNT = 10
MAX_LENGTH_SHORT_URL = 6
CHAR_SELECT = string.digits + string.ascii_letters
