from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

import drf_link_header_pagination

from .mocks import MockObject, MockQuerySet
from .test_link_header_cursor_pagination import TestLinkHeaderCursorPagination

factory = APIRequestFactory()


class TestLinkHeaderLinkResponseCursorPagination(TestLinkHeaderCursorPagination):
    """
    Unit tests for `pagination.LinkHeaderLinkResponseCursorPagination`.
    """

    def setup(self):
        class ExamplePagination(
            drf_link_header_pagination.LinkHeaderLinkResponseCursorPagination
        ):
            page_size = 5
            page_size_query_param = "page_size"
            max_page_size = 20
            ordering = "created"

        self.pagination = ExamplePagination()
        self.queryset = MockQuerySet(
            [MockObject(idx) for idx in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]]
        )

    def test_no_cursor(self):
        url = "/"
        request = Request(factory.get(url))
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        response_next_url = response.data["next"]
        response_previous_url = response.data["previous"]
        (previous_url, next_url) = self.get_page_urls(url)
        assert response_next_url == next_url
        assert response_previous_url == previous_url
        response_data_values = [item.value for item in response.data["results"]]
        assert response_data_values == [1, 2, 3, 4, 5]

    def test_second_page(self):
        first_page_url = "/"
        (_, second_page_url) = self.get_page_urls(first_page_url)

        request = Request(factory.get(second_page_url))
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        response_next_url = response.data["next"]
        response_previous_url = response.data["previous"]
        (previous_url, next_url) = self.get_page_urls(second_page_url)
        assert response_next_url == next_url
        assert response_previous_url == previous_url
        response_data_values = [item.value for item in response.data["results"]]
        assert response_data_values == [6, 7, 8, 9, 10]
