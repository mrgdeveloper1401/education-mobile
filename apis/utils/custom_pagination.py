from rest_framework.pagination import PageNumberPagination


class TwentyPageNumberPagination(PageNumberPagination):
    page_size = 20
