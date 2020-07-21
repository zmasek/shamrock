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

Methods
~~~~~~~

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

Single Item
~~~~~~~~~~~

You can also query a specific item from the database::

    api.plants(103505)

Search
~~~~~~

Searching is covered with a separate method bound to a plant/search endpoint::

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

You can use the varoius query string options described on Trefle API documentation as keyword
arguments in methods::

    api.species(common_name="blackwood")
