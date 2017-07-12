from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param

__version__ = '0.1.1'

__all__ = [
    'LinkHeaderPagination',
]


class LinkHeaderPagination(PageNumberPagination):
    """ Inform the user of pagination links via response headers, similar to
    what's described in
    https://developer.github.com/guides/traversing-with-pagination/.
    """
    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()
        first_url = self.get_first_link()
        last_url = self.get_last_link()

        links = []
        for url, label in (
            (first_url, 'first'),
            (previous_url, 'prev'),
            (next_url, 'next'),
            (last_url, 'last'),
        ):
            if url is not None:
                links.append('<{}>; rel="{}"'.format(url, label))

        headers = {'Link': ', '.join(links)} if links else {}

        return Response(data, headers=headers)

    def get_first_link(self):
        if not self.page.has_previous():
            return None
        else:
            url = self.request.build_absolute_uri()
            return remove_query_param(url, self.page_query_param)

    def get_last_link(self):
        if not self.page.has_next():
            return None
        else:
            url = self.request.build_absolute_uri()
            return replace_query_param(
                url,
                self.page_query_param,
                self.page.paginator.num_pages,
            )
