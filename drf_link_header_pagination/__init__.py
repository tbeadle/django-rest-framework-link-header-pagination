from rest_framework.pagination import CursorPagination, PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param

__all__ = [
    "LinkHeaderPagination",
    "LinkHeaderLimitOffsetPagination",
    "LinkHeaderCursorPagination",
    "LinkHeaderLinkResponseCursorPagination",
]


class LinkHeaderMixin:
    def get_headers(self):
        """Prepare and return link headers."""
        links = []
        for label, method_name in (
            ("prev", "get_previous_link"),
            ("next", "get_next_link"),
            ("first", "get_first_link"),
            ("last", "get_last_link"),
        ):
            try:
                method = getattr(self, method_name)
            except AttributeError:
                continue
            links.append((method(), label))

        header_links = []
        for url, label in links:
            if url is not None:
                header_links.append('<{}>; rel="{}"'.format(url, label))

        return {"Link": ", ".join(header_links)} if header_links else {}

    def get_paginated_response(self, data):
        return Response(data, headers=self.get_headers())


class LinkHeaderLimitOffsetPagination(LinkHeaderMixin, LimitOffsetPagination):
    """
    Link header pagination with offset/limit links. Implements the regular
    `LimitOffsetPagination` module with `Link: ` headers instead.
    """
    def get_first_link(self):
        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.limit_query_param, self.limit)

        return remove_query_param(url, self.offset_query_param)

    def get_last_link(self):
        if not self.get_next_link():
            return None

        # We need to adjust for 0 offset, otherwise we'll get the last link
        # to an empty page if count % limit == 0 (i.e. the "pages" line up
        # exactly)
        offset = max(0, self.count - ((self.count - 1) % self.limit) - 1)

        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.limit_query_param, self.limit)

        return replace_query_param(url, self.offset_query_param, offset)

    def get_paginated_response_schema(self, schema):
        return schema


class LinkHeaderPagination(LinkHeaderMixin, PageNumberPagination):
    """Inform the user of pagination links via response headers, similar to
    what's described in
    https://developer.github.com/guides/traversing-with-pagination/.
    """

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

    def get_paginated_response_schema(self, schema):
        return schema


class LinkHeaderCursorPagination(LinkHeaderMixin, CursorPagination):
    """
    Customized cursor pagination with links provided via:
        - headers.
    """

    def get_paginated_response_schema(self, schema):
        return schema


class LinkHeaderLinkResponseCursorPagination(LinkHeaderMixin, CursorPagination):
    """
    Customized cursor pagination with links provided via:
        - content of the response
        - headers.
    """

    def get_paginated_response(self, data):
        return super().get_paginated_response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
