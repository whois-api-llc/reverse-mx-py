.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :alt: reverse-mx-py license
    :target: https://opensource.org/licenses/MIT

.. image:: https://img.shields.io/pypi/v/reverse-mx.svg
    :alt: reverse-mx-py release
    :target: https://pypi.org/project/reverse-mx

.. image:: https://github.com/whois-api-llc/reverse-mx-py/workflows/Build/badge.svg
    :alt: reverse-mx-py build
    :target: https://github.com/whois-api-llc/reverse-mx-py/actions

========
Overview
========

The client library for
`Reverse MX API <https://reverse-mx.whoisxmlapi.com/>`_
in Python language.

The minimum Python version is 3.6.

Installation
============

.. code-block:: shell

    pip install reverse-mx

Examples
========

Full API documentation available `here <https://reverse-mx.whoisxmlapi.com/api/documentation/making-requests>`_

Create a new client
-------------------

.. code-block:: python

    from reversemx import *

    client = Client('Your API key')

Make basic requests
-------------------

.. code-block:: python

    # Get the number of domains.
    result = client.data('aspmx.l.google.com')
    print(result.size)

    # Get raw API response
    raw_result = client.raw_data(
        "aspmx.l.google.com",
        response_format=Client.XML_FORMAT
    )

Advanced usage
-------------------

Extra request parameters

.. code-block:: python

    result = client.data("aspmx.l.google.com", search_from="9")

    resp = client.data("aspmx.l.google.com")
    if resp.has_next():
        next_page = client.next_page("aspmx.l.google.com", resp)

    for page in client.iterate_pages("aspmx.l.google.com"):
        print(page)