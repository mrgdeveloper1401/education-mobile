from rest_framework.pagination import PageNumberPagination


class TwentyPageNumberPagination(PageNumberPagination):
    page_size = 20


class ScrollPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100
    page_size_query_param = 'page_size'
