pipenv --three
pipenv install --dev
pipenv run coverage run --source . tests && pipenv run coverage report -m
mkdir docs
cd docs
pipenv run spinx-quickstart
pipenv run sphinx-autodoc -f -o source/ ../shamrock/ 
TODO: add coveralls, add CI

===============================
Shamrock - A Trefle API Library
===============================

Usage:
api = Shamrock('mytoken')
api.species()
