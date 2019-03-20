pipenv --three
pipenv install --dev
pipenv run coverage run --source . tests && pipenv run coverage report -m

TODO: add coveralls, add CI

===============================
Shamrock - A Trefle API Library
===============================

Usage:
api = Shamrock('mytoken')
api.species()
