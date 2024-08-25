from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class LimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'  # Название параметра для лимита
    max_page_size = 100  # Максимально допустимый размер страницы


class SubLimitPagination(LimitOffsetPagination):
    page_size_query_param = 'limit'
    #default_limit = 10  # Значение по умолчанию
    max_limit = 100  # Максимальное значение limit
