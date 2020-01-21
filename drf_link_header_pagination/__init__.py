from collections import OrderedDict

from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param

__version__ = "0.1.2"

__all__ = [
    "LinkHeaderPagination",
    "LinkHeaderCursorPagination",
    "LinkHeaderJsonKeyCursorPagination",
]


class LinkHeaderMixin:
    def get_headers(self):
        """Prepare and return link headers."""
        links = ((self.get_previous_link(), "prev"), (self.get_next_link(), "next"))

        if hasattr(self, "get_first_link") and hasattr(self, "get_last_link"):
            links = (
                *links,
                (self.get_first_link(), "first"),
                (self.get_last_link(), "last"),
            )

        header_links = []
        for url, label in links:
            if url is not None:
                header_links.append('<{}>; rel="{}"'.format(url, label))

        return {"Link": ", ".join(header_links)} if header_links else {}


class LinkHeaderPagination(LinkHeaderMixin, PageNumberPagination):
    """ Inform the user of pagination links via response headers, similar to
    what's described in
    https://developer.github.com/guides/traversing-with-pagination/.
    """

    def get_paginated_response(self, data):
        return Response(data, headers=self.get_headers())

    def get_first_link(self):
        if not self.page.has_previous():
            return None

        url = self.request.build_absolute_uri()

        return remove_query_param(url, self.page_query_param)

    def get_last_link(self):
        if not self.page.has_next():
            return None

        url = self.request.build_absolute_uri()

        return replace_query_param(
            url, self.page_query_param, self.page.paginator.num_pages
        )


class LinkHeaderCursorPagination(LinkHeaderMixin, CursorPagination):
    """
    Customized cursor pagination class utilizing Link header.
    Provides standard json key pagination links in addition to LinkHeader.
    """

    def get_paginated_response(self, data):
        return Response(data, headers=self.get_headers())


class LinkHeaderJsonKeyCursorPagination(LinkHeaderMixin, CursorPagination):
    """
    Provides cursor pagination with standard json key pagination links in
    addition to LinkHeader.
    """

    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()

        return Response(
            OrderedDict(
                [("next", next_url), ("previous", previous_url), ("results", data)]
            ),
            headers=self.get_headers(),
        )
