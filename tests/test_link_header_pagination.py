# coding: utf-8
from __future__ import unicode_literals

import pytest
from django.test import override_settings
from rest_framework import exceptions
from rest_framework.pagination import PAGE_BREAK, PageLink
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

import drf_link_header_pagination

factory = APIRequestFactory()


class TestLinkHeaderPagination:
    """
    Unit tests for `pagination.LinkHeaderPagination`.
    """

    def setup(self):
        class ExamplePagination(drf_link_header_pagination.LinkHeaderPagination):
            page_size = 5

        self.pagination = ExamplePagination()
        self.queryset = range(1, 101)

    def paginate_queryset(self, request):
        return list(self.pagination.paginate_queryset(self.queryset, request))

    def get_paginated_response(self, queryset):
        return self.pagination.get_paginated_response(queryset)

    def get_html_context(self):
        return self.pagination.get_html_context()

    @override_settings(ALLOWED_HOSTS=["testserver"])
    def test_no_page_number(self):
        request = Request(factory.get("/"))
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        context = self.get_html_context()
        assert queryset == [1, 2, 3, 4, 5]
        assert response.data == [1, 2, 3, 4, 5]
        assert response["Link"] == (
            '<http://testserver/?page=2>; rel="next", '
            '<http://testserver/?page=20>; rel="last"'
        )
        assert context == {
            "previous_url": None,
            "next_url": "http://testserver/?page=2",
            "page_links": [
                PageLink("http://testserver/", 1, True, False),
                PageLink("http://testserver/?page=2", 2, False, False),
                PageLink("http://testserver/?page=3", 3, False, False),
                PAGE_BREAK,
                PageLink("http://testserver/?page=20", 20, False, False),
            ],
        }
        assert self.pagination.display_page_controls
        assert isinstance(self.pagination.to_html(), type(""))

    @override_settings(ALLOWED_HOSTS=["testserver"])
    def test_second_page(self):
        request = Request(factory.get("/", {"page": 2}))
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        context = self.get_html_context()
        assert queryset == [6, 7, 8, 9, 10]
        assert response.data == [6, 7, 8, 9, 10]
        assert response["Link"] == (
            '<http://testserver/>; rel="prev", '
            '<http://testserver/?page=3>; rel="next", '
            '<http://testserver/>; rel="first", '
            '<http://testserver/?page=20>; rel="last"'
        )
        assert context == {
            "previous_url": "http://testserver/",
            "next_url": "http://testserver/?page=3",
            "page_links": [
                PageLink("http://testserver/", 1, False, False),
                PageLink("http://testserver/?page=2", 2, True, False),
                PageLink("http://testserver/?page=3", 3, False, False),
                PAGE_BREAK,
                PageLink("http://testserver/?page=20", 20, False, False),
            ],
        }

    @override_settings(ALLOWED_HOSTS=["testserver"])
    def test_last_page(self):
        request = Request(factory.get("/", {"page": "last"}))
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        context = self.get_html_context()
        assert queryset == [96, 97, 98, 99, 100]
        assert response.data == [96, 97, 98, 99, 100]
        assert response["Link"] == (
            '<http://testserver/?page=19>; rel="prev", '
            '<http://testserver/>; rel="first"'
        )
        assert context == {
            "previous_url": "http://testserver/?page=19",
            "next_url": None,
            "page_links": [
                PageLink("http://testserver/", 1, False, False),
                PAGE_BREAK,
                PageLink("http://testserver/?page=18", 18, False, False),
                PageLink("http://testserver/?page=19", 19, False, False),
                PageLink("http://testserver/?page=20", 20, True, False),
            ],
        }

    def test_invalid_page(self):
        request = Request(factory.get("/", {"page": "invalid"}))
        with pytest.raises(exceptions.NotFound):
            self.paginate_queryset(request)
