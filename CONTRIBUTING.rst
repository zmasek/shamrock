============
Contributing
============

Every contribution is welcome. If not with the concrete pull request, then as:

#. A mention on the social media
#. Giving any kind of feedback on the communication channels
#. A bug report on https://github.com/zmasek/shamrock/issues
    #. Make sure it's not a duplicate of a bug already reported
    #. Include operating system name and version, essentially, the environment you're running
    #. How to reproduce the bug in detail
    #. What were you trying to do
    #. What did you expect to happen
    #. Include screenshots if necessary
    #. Help us help you
#. Fix existing bugs and implement new features
    #. Fork the repository
    #. Clone it locally
    #. cd into the repository
    #. pipenv install --dev (make sure that pipenv is installed on your system first)
    #. pipenv run pre-commit install
    #. If you want to test it from the environment: pipenv run python setup.py develop
    #. Make modifications
    #. pipenv run coverage run --source . tests && pipenv run coverage report -m
    #. It is easier if you keep commits isolated properly. It helps you get your PR merged
    #. Before making a pull request make sure:
        #. You have the docs updated
        #. The tests are added/changed if necessary
        #. The test pass successfuly
        #. You add yourself in the AUTHORS.rst as a contributor
    #. Push back and submit a pull request
#. Do the same for expanding the documentation. A project is only as good as its documentation
