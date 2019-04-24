Setting up
==========

Prerequisites
-------------

Shamrock relies on Python 3.6 and above and `Requests III <https://3.python-requests.org/>`_
library. Requests will get installed automatically, but you need to make sure to meet the other
requirement.

To start interacting with the API, you'll need a token from them. Obtaining it is not a big deal.
Make sure to sign up on the Trefle page and obtain token there. You'll need it when using the
library.

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
    api = Shamrock('my_secret_token')
