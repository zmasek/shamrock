===============================
Shamrock - A Trefle API Library
===============================

.. image:: https://coveralls.io/repos/github/zmasek/shamrock/badge.svg?branch=master
   :target: https://coveralls.io/github/zmasek/shamrock?branch=master
   :alt: Coverage Status

.. image:: https://readthedocs.org/projects/shamrock/badge/?version=latest
    :target: https://shamrock.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

☘ **Shamrock** is a Python shallow API library for `Trefle <https://trefle.io/>`_ integration. It
enables interacting with the Trefle plants API in Python to get the information needed for various
things you might want to use the API with such as research, gardening software, automation, etc. It
is made for use with Python 3.6 and above.

For the full documentation refer to
`Shamrock documentation <https://shamrock.readthedocs.io/en/latest/>`_.

For more information what the Trefle service provides, refer to the
`Trefle API documentation <https://trefle.io/reference>`_. It is also useful for checking out how to
use the API with Shamrock library.

Installation
------------
::

    pipenv install shamrock

or ::

    pip install shamrock

Simple Usage Example
--------------------
::

    from shamrock import Shamrock
    api = Shamrock('mytoken')
    species = api.species()


Advanced Usage
--------------

You can configure the API initially like this::

    api = Shamrock(TOKEN)

Methods that can be run with the API are::

    api.kingdoms()
    api.subkingdoms()
    api.divisions()
    api.division_classes()
    api.division_orders()
    api.families()
    api.genus()
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

You can also use the varoius query string options described on Trefle API documentation as keyword
arguments in methods, however, be careful when unpacking filters, for example::

    filters = {"filter[common_name]" : "blackwood"}
    api.species(**filters)
