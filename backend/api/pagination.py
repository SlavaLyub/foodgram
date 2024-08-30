from rest_framework.pagination import PageNumberPagination

from foodgram.constants import PAGINATION_LIMIT


class LimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    max_page_size = PAGINATION_LIMIT
