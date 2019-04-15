===============================
Shamrock - A Trefle API Library
===============================

.. image:: https://coveralls.io/repos/bitbucket/zmasek/shamrock/badge.svg?branch=master
   :target: https://coveralls.io/bitbucket/zmasek/shamrock?branch=master
   :alt: Coverage Status

**Shamrock** is a Python shallow API library for `Trefle <https://trefle.io/>`_ integration.

Simple usage example::

    from shamrock import Shamrock
    api = Shamrock('mytoken')
    api.species()

-------------
Contributing:
-------------

1. Fork the repository
2. Clone it locally
3. cd into the repository
4. pipenv install --dev (make sure that pipenv is installed on your system first)
5. make modifications
6. pipenv run coverage run --source . tests && pipenv run coverage report -m
7. push back and submit a pull request
