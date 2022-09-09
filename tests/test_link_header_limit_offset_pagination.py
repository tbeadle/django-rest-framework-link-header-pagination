import pytest
from rest_framework import exceptions
from rest_framework.pagination import PAGE_BREAK, PageLink
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

import drf_link_header_pagination

factory = APIRequestFactory()


class TestLinkHeaderLimitOffsetPagination:
    """
    Unit tests for `pagination.LinkHeaderLimitOffsetPagination`.
    """
    def setup(self):
        class ExamplePagination(drf_link_header_pagination.LinkHeaderLimitOffsetPagination):
            default_limit = 4

        self.pagination = ExamplePagination()
        self.queryset = range(1, 101)

    def paginate_queryset(self, request):
        return list(self.pagination.paginate_queryset(self.queryset, request))

    def get_paginated_response(self, queryset):
        return self.pagination.get_paginated_response(queryset)

    def get_html_context(self):
        return self.pagination.get_html_context()

    def test_no_offset(self):
        request = Request(factory.get("/"))
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        context = self.get_html_context()

        assert queryset == [1, 2, 3, 4]
        assert response.data == [1, 2, 3, 4]
        assert response["Link"] == (
            '<http://testserver/?limit=4&offset=4>; rel="next", '
            '<http://testserver/?limit=4>; rel="first", '
            '<http://testserver/?limit=4&offset=96>; rel="last"'
        )

        assert context == {
            "previous_url": None,
            "next_url": "http://testserver/?limit=4&offset=4",
            "page_links": [
                PageLink("http://testserver/", 1, True, False),
                PageLink("http://testserver/?offset=4", 2, False, False),
                PageLink("http://testserver/?offset=8", 3, False, False),
                PAGE_BREAK,
                PageLink("http://testserver/?offset=96", 25, False, False),
            ],
        }
        assert self.pagination.display_page_controls
        assert isinstance(self.pagination.to_html(), type(""))

    def test_second_page(self):
        request = Request(factory.get("/", {"offset": 4}))
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        context = self.get_html_context()

        assert queryset == [5, 6, 7, 8]
        assert response.data == [5, 6, 7, 8]
        assert response["Link"] == (
            '<http://testserver/?limit=4>; rel="prev", '
            '<http://testserver/?limit=4&offset=8>; rel="next", '
            '<http://testserver/?limit=4>; rel="first", '
            '<http://testserver/?limit=4&offset=96>; rel="last"'
        )
        assert context == {
            "previous_url": "http://testserver/?limit=4",
            "next_url": "http://testserver/?limit=4&offset=8",
            "page_links": [
                PageLink("http://testserver/", 1, False, False),
                PageLink("http://testserver/?offset=4", 2, True, False),
                PageLink("http://testserver/?offset=8", 3, False, False),
                PAGE_BREAK,
                PageLink("http://testserver/?offset=96", 25, False, False),
            ],
        }

    def test_last_page(self):
        request = Request(factory.get("/", {"offset": "96"}))
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        context = self.get_html_context()
        assert queryset == [97, 98, 99, 100]
        assert response.data == [97, 98, 99, 100]
        assert response["Link"] == (
            '<http://testserver/?limit=4&offset=92>; rel="prev", '
            '<http://testserver/?limit=4>; rel="first"'
        )
        assert context == {
            "previous_url": "http://testserver/?limit=4&offset=92",
            "next_url": None,
            "page_links": [
                PageLink("http://testserver/", 1, False, False),
                PAGE_BREAK,
                PageLink("http://testserver/?offset=88", 23, False, False),
                PageLink("http://testserver/?offset=92", 24, False, False),
                PageLink("http://testserver/?offset=96", 25, True, False),
            ],
        }
