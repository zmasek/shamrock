Setting up
==========

Prerequisites
-------------

Shamrock relies on Python 3.6 and above, and `Requests III <https://3.python-requests.org/>`_
library. Requests will get installed automatically, but you need to make sure to meet the other
requirements.

To start interacting with the API, you'll need a token. Obtaining it is not a big deal if you know where to look.
Make sure to sign up where you need to and obtain token. You'll need it when using the library.

Installation
------------

It is highly recommended to start using `pipenv <https://pipenv.readthedocs.io/en/latest/>`_ for
managing your dependencies::

    $ pipenv install shamrock

but you can use pip also::

    $ pip install shamrock

Basic Usage
-----------
::

    from shamrock import Shamrock
    api = Shamrock('my_secret_token', 'trefle_replacement_url')
