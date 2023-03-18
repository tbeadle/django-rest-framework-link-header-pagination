# djangorestframework-link-header-pagination

![build-status-image][build-status-image] ![pypi-version][pypi-version]

## Overview

Provide pagination using a `Link` HTTP header as described in [GitHub's REST API documentation][github-pagination].

This pagination style accepts a single page number in the request query parameters. The response uses an HTTP header called `Link` to provide the URLs for the next, previous, first, and last pages. If you are using Python's [Requests][requests] library to make the request, this header is automatically parsed for you as described [here][requests-link-header].

**Request**:

    GET https://api.example.org/accounts/?page=4

**Response**:

    HTTP 200 OK
    Link: <https://api.example.org/accounts/>; rel="first", <https://api.example.org/accounts/?page=3>; rel="prev", <https://api.example.org/accounts/?page=5>; rel="next", <https://api.example.org/accounts/?page=11>; rel="last"

    [
       {
           "id": 1,
           "name": "item one",
       },
       ...
    ]

## Requirements

 -  Python (3.7+)
 -  Django (3.2+)
 -  Django REST Framework (3.11+)

## Installation

Install using ``pip``:

```bash
$ pip install djangorestframework-link-header-pagination
```

## Setup

Add `drf_link_header_pagination` to your project's `INSTALLED_APPS` setting.

To enable the `LinkHeaderPagination` style globally, use the following configuration, modifying the `PAGE_SIZE` as desired:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'drf_link_header_pagination.LinkHeaderPagination',
    'PAGE_SIZE': 100
}
```

On `GenericAPIView` subclasses you may also set the `pagination_class` attribute to select `LinkHeaderPagination` on a per-view basis.

Other pagination classes that are available are:

- `LinkHeaderCursorPagination`: This is similar to the normal [`CursorPagination`][cursor-pagination] class but using the `Link` header to return only the `next` and/or `prev` links. The `first` and `last` links are unavailable.
- `LinkHeaderLinkResponseCursorPagination`: This is similar to
  `LinkHeaderCursorPagination`, but in addition to the `next` and/or `prev` URL's being in the `Link` header, the content of the response body is updated to include them as well. The body will be an object with the keys `next` (the next page's URL or None), `previous` (the previous page's URL or None), and `results` (the original content of the body).
- `LinkHeaderLimitOffsetPagination`: [Uses the `LimitOffsetPagination` pagination class from DRF](https://www.django-rest-framework.org/api-guide/pagination/#limitoffsetpagination) to support `offset` and `limit` parameters instead of `page` to indicate offset into the queryset. 

## Configuration

The configuration is the same as for
[`PageNumberPagination`](page-number-pagination-configuration).

## Testing

Use the excellent [tox](tox) testing tool to run the tests
against all supported versions of Python and Django. Install tox
globally, and then simply run:

```bash
$ tox
```

[build-status-image]: https://secure.travis-ci.org/tbeadle/django-rest-framework-link-header-pagination.svg?branch=master
[pypi-version]: https://img.shields.io/pypi/v/djangorestframework-link-header-pagination.svg
[github-pagination]: https://docs.github.com/en/rest/guides/traversing-with-pagination
[requests]: http://docs.python-requests.org
[requests-link-header]: http://docs.python-requests.org/en/master/user/advanced/#link-headers
[page-number-pagination-configuration]: http://www.django-rest-framework.org/api-guide/pagination/#pagenumberpagination
[cursor-pagination]: https://www.django-rest-framework.org/api-guide/pagination/#cursorpagination
[tox]: http://tox.readthedocs.org/en/latest/
