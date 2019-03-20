import urllib
import requests

ENDPOINTS = (
    'kingdoms',
    'subkingdoms',
    'divisions',
    'families',
    'genuses',
    'plants',
    'species',
)


class Shamrock(object):
    def __init__(self, token, page_size=None):
        self.url = 'https://trefle.io/api/'
        self.headers = {'Authorization': 'Bearer {}'.format(token)}
        self.page_size = page_size
        self.result = None

    def __getattr__(self, attr):
        if attr in ENDPOINTS:
            def wrapper(*args, **kwargs):
                return self.ENDPOINT(attr, *args, **kwargs)
            return wrapper
        raise AttributeError

    def _get_full_url(self, endpoint):
        return '{}{}'.format(self.url, endpoint)

    def _kwargs(self, endpoint, **query_parameters):
        kwargs = {
            'url': endpoint if endpoint.startswith('http') else self._get_full_url(endpoint),
            'headers': self.headers
        }
        if self.page_size is not None:
            kwargs['params'] = {'page_size': self.page_size}
        if query_parameters:
            if 'params' in kwargs:
                kwargs['params'].update(dict(**query_parameters))
            else:
                kwargs['params'] = dict(**query_parameters)
        return kwargs

    def _get_parametrized_url(self, kwargs):
        try:
            params = urllib.parse.urlencode(kwargs['params'], quote_via=urllib.parse.quote_plus)
            return '{}?{}'.format(kwargs['url'], params)
        except KeyError:
            return kwargs['url']

    def _get_result(self, kwargs):
        if self.result is not None:
            built_url = self._get_parametrized_url(kwargs)
            if built_url == self.result.url:
                return self.result.json()
        self.result = requests.get(**kwargs)
        return self.result.json()

    def search(self, q, **kwargs):
        query_parameters = {'q': q}
        query_parameters.update(dict(**kwargs))
        kwargs = self._kwargs('species', **query_parameters)
        return self._get_result(kwargs)

    def ENDPOINT(self, endpoint, pk=None, **kwargs):
        kwargs = self._kwargs('{}/{:d}'.format(endpoint, pk) if pk else endpoint)
        return self._get_result(kwargs)

    def next(self):
        if 'next' in self.result.links:
            kwargs = self._kwargs(self.result.links['next']['url'])
            self.result = requests.get(**kwargs)
            return self.result.json()

    def previous(self):
        if 'prev' in self.result.links:
            kwargs = self._kwargs(self.result.links['prev']['url'])
            self.result = requests.get(**kwargs)
            return self.result.json()

    def first(self):
        if 'first' in self.result.links:
            kwargs = self._kwargs(self.result.links['first']['url'])
            self.result = requests.get(**kwargs)
            return self.result.json()

    def last(self):
        if 'last' in self.result.links:
            kwargs = self._kwargs(self.result.links['last']['url'])
            self.result = requests.get(**kwargs)
            return self.result.json()
