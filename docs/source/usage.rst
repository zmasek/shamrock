Usage
=====

Basic
-----
::

    from shamrock import Shamrock
    api = Shamrock('my_secret_token')
    plants = api.plants()
    print(plants)

Advanced
--------

Setting Up
~~~~~~~~~~
::

    from shamrock import Shamrock
    api = Shamrock('my_secret_token')

or with a configuration::

    from shamrock import Shamrock
    api = Shamrock('my_secret_token', page_size=5)

Methods
~~~~~~~

Methods that can be run with the API are::

    api.kingdoms()
    api.subkingdoms()
    api.divisions()
    api.families()
    api.genuses()
    api.plants()
    api.species()

They correspond to the Trefle API endpoints.

Single item
~~~~~~~~~~~

You can also query a specific item from the database::

    api.plants(103505)

Search
~~~~~~

Searching is covered with a separate method::

    api.search("tomato")

Navigation
~~~~~~~~~~

Navigating the API is covered with these methods::

    api.next()
    api.prev()
    api.first()
    api.last()

It will work only if you previously made a request. For example::

    api.species()
    api.next()

Specific Options
~~~~~~~~~~~~~~~~

By default, the API responds with the list of whatever number is set in the Trefle. You can
manipulate it with previously mentioned page_size::

    api.species(page_size=5)

You can also use the varoius query string options described on Trefle API documentation as keyword
arguments in methods::

    api.species(common_name="blackwood")
