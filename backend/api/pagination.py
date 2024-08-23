from rest_framework.pagination import PageNumberPagination


class LimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'  # Название параметра для лимита
    max_page_size = 100  # Максимально допустимый размер страницы
