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

Basic methods that can be run with the API are::

    api.kingdoms()
    api.subkingdoms()
    api.divisions()
    api.division_classes()
    api.division_orders()
    api.families()
    api.genus()
    api.plants()
    api.species()
    api.distributions()

They correspond to the Trefle API endpoints.

Advanced methods exist and are explained below.

Single Item
~~~~~~~~~~~

You can also query a specific item from the database::

    api.plants(103505)

Or with a slug instead::

    api.species("solanum-lycopersicum")

Search
~~~~~~

Searching is covered with a separate method bound to a plants/search endpoint::

    api.search("tomato")

But if you want to search through species (species/search), use the same method, but specify it::

    api.search("tomato", what="species")

Reporting Errors
~~~~~~~~~~~~~~~~

Reporting an error is done through a report_error method that requires two positional arguments.

    api.report_error(103505, "A sentence of what is wrong")

The first argument is describing what is wrong, the second argument is either a slug or an id of the
entry in question. By default, it is reporting a plant entry, but can be overriden to report an
error of the species as well like so::

    api.report_error("chenopodium-album", "A sentence of what is wrong", what="species")

You can also submit a full correction, or a correction of the specific fields on the specified entry
through a general endpoint like this::

    json_body = {

    }
    api.corrections("abies-alba", json_body)

or::

    api.corrections(1164724, json_body)

But you can also list all the corrections or look for a specific one. Note that in this case, you
are providing an id of the correction, not of the species.::

    api.corrections()
    api.corrections(1)

For the instructions on
`how to submit a correction <https://docs.trefle.io/docs/advanced/complete-data>`_ check out the
Trefle section on it.

Retrieving plants by distribution or genus
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is a separate method for retrieving plants by distribution or genus and takes that identifier
like so::

    api.plants_by("distributions", 286)
    api.plants_by("genus", "aalius")

The second argument is either an id of the modifier or a slug.

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
arguments in methods, however, be careful when unpacking filters because they come with brackets, so
for example::

    filters = {"filter[common_name]": "blackwood"}
    api.species(**filters)

Or something simpler like a direct page::

    api.species(page=3)

To order, do it like this::

    ordering = {"order[common_name]": "asc"}
    api.species(**ordering)

Client Authentication
~~~~~~~~~~~~~~~~~~~~~

While it's easy to obtain a token from Trefle and use the library on the server, it becomes tricky
when one wants to use it on the browser side. This is achieved by periodically obtaining JWT token.

It is still a server call because the common token needs to be provided. Once the Shamrock is
initialized, using a normal token, this is called to obtain a JWT::

    api.auth(origin="https://example.com")

An argument called ip can be specified if needed, but the above should cover the basics. The result
will have the token key along with expiry that needs to be tracked.

Exceptions
~~~~~~~~~~

There is a ShamrockException that covers most of the cases should one want to use it. It can be
imported from the exception module.
