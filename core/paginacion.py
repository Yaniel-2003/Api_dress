from rest_framework.pagination import PageNumberPagination


class PaginacionGlobal(PageNumberPagination):
    page_size = 50
    pague_size_query_param = 'page_size'
    max_page_size = 100