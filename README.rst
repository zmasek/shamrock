===============================
Shamrock - A Trefle API Library
===============================

.. image:: https://coveralls.io/repos/github/zmasek/shamrock/badge.svg?branch=master
   :target: https://coveralls.io/github/zmasek/shamrock?branch=master
   :alt: Coverage Status

**Shamrock** is a Python shallow API library for `Trefle <https://trefle.io/>`_ integration. It
enables interacting with the Trefle plants API in Python to get the information needed for various
things you might want to use the API with such as research, gardening software, automation, etc. It
is made for use with Python 3.6 and above.

Installation
------------
::

    pipenv install shamrock

or ::

    pip install shamrock

Simple usage example
--------------------
::

    from shamrock import Shamrock
    api = Shamrock('mytoken')
    species = api.species()


Advanced usage
--------------

You can configure the API initially like this::

    api = Shamrock(TOKEN, page_size=10)

Currently, page_size is the only available option.

Methods that can be run with the API are::

    api.kingdoms()
    api.subkingdoms()
    api.divisions()
    api.families()
    api.genuses()
    api.plants()
    api.species()

They correspond to the Trefle API endpoints.

You can also query a specific item from the database::

    api.plants(103505)

Searching is covered with a separate method::

    api.search("tomato")

Navigating the API is covered with these methods::

    api.next()
    api.prev()
    api.first()
    api.last()

It will work only if you previously made a request. For example::

    api.species()
    api.next()

By default, the API responds with the list of whatever number is set in the Trefle. You can
manipulate it with previously mentioned page_size::

    api.species(page_size=5)

You can also use the varoius query string options described on Trefle API documentation as keyword
arguments in methods::

    api.species(common_name="blackwood")
