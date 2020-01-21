# coding: utf-8
from __future__ import unicode_literals

import pytest
from django.test import override_settings
from rest_framework import exceptions
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

import drf_link_header_pagination

from .mocks import MockObject, MockQuerySet

factory = APIRequestFactory()


class TestLinkHeaderCursorPagination:
    """
    Unit tests for `pagination.LinkHeaderCursorPagination`.

    Tests inspired from:
        https://github.com/encode/django-rest-framework/blob/master/tests/test_pagination.py
    """

    def setup(self):
        class ExamplePagination(drf_link_header_pagination.LinkHeaderCursorPagination):
            page_size = 5
            page_size_query_param = "page_size"
            max_page_size = 20
            ordering = "created"

        self.pagination = ExamplePagination()
        self.queryset = MockQuerySet(
            [
                MockObject(idx)
                for idx in [
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    2,
                    3,
                    4,
                    4,
                    4,
                    4,
                    5,
                    6,
                    7,
                    7,
                    7,
                    7,
                    7,
                    7,
                    7,
                    7,
                    7,
                    8,
                    9,
                    9,
                    9,
                    9,
                    9,
                    9,
                ]
            ]
        )

    def get_pages(self, url):
        """
        Given a URL return a tuple of:
        (previous page, current page, next page, previous url, next url)
        """
        request = Request(factory.get(url))
        queryset = self.pagination.paginate_queryset(self.queryset, request)
        current = [item.created for item in queryset]

        next_url = self.pagination.get_next_link()
        previous_url = self.pagination.get_previous_link()

        if next_url is not None:
            request = Request(factory.get(next_url))
            queryset = self.pagination.paginate_queryset(self.queryset, request)
            next = [item.created for item in queryset]
        else:
            next = None

        if previous_url is not None:
            request = Request(factory.get(previous_url))
            queryset = self.pagination.paginate_queryset(self.queryset, request)
            previous = [item.created for item in queryset]
        else:
            previous = None

        return (previous, current, next, previous_url, next_url)

    def paginate_queryset(self, request):
        return list(self.pagination.paginate_queryset(self.queryset, request))

    def get_paginated_response(self, queryset):
        return self.pagination.get_paginated_response(queryset)

    def get_html_context(self):
        return self.pagination.get_html_context()

    @override_settings(ALLOWED_HOSTS=["testserver"])
    def test_no_cursor(self):
        url = "/"
        request = Request(factory.get(url))
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        context = self.get_html_context()
        queryset_values = [item.value for item in queryset]
        response_data_values = [item.value for item in response.data]
        (previous, current, next, previous_url, next_url) = self.get_pages(url)
        assert queryset_values == [1, 1, 1, 1, 1]
        assert response_data_values == [1, 1, 1, 1, 1]
        assert response["Link"] == ('<{}>; rel="next"'.format(next_url))
        assert context == {
            "previous_url": None,
            "next_url": next_url,
        }
        assert self.pagination.display_page_controls
        assert isinstance(self.pagination.to_html(), type(""))

    @override_settings(ALLOWED_HOSTS=["testserver"])
    def test_second_page(self):
        first_page_url = "/"
        (_, _, _, _, second_page_url) = self.get_pages(first_page_url)

        request = Request(factory.get(second_page_url))
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        context = self.get_html_context()
        queryset_values = [item.value for item in queryset]
        response_data_values = [item.value for item in response.data]
        (_, _, _, previous_url, next_url) = self.get_pages(second_page_url)
        assert queryset_values == [1, 2, 3, 4, 4]
        assert response_data_values == [1, 2, 3, 4, 4]
        assert response["Link"] == ('<{}>; rel="prev", <{}>; rel="next"').format(
            previous_url, next_url
        )
        assert context == {
            "previous_url": previous_url,
            "next_url": next_url,
        }

    @override_settings(ALLOWED_HOSTS=["testserver"])
    def test_invalid_page(self):
        request = Request(factory.get("/", {"cursor": "invalid"}))
        with pytest.raises(exceptions.NotFound):
            self.paginate_queryset(request)
