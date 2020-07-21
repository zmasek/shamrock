# -*- coding: utf-8 -*-

"""Shamrock - A Trefle API Integration."""
import logging
from typing import Any, Callable, Dict, Optional, Tuple
from urllib import parse

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError, Timeout, TooManyRedirects
from requests.packages.urllib3.util.retry import Retry

ENDPOINTS: Tuple[str, str, str, str, str, str, str] = (
    "kingdoms",
    "subkingdoms",
    "divisions",
    "families",
    "genuses",
    "plants",
    "species",
)
NAVIGATION: Tuple[str, str, str, str] = ("next", "prev", "first", "last")
logger: logging.Logger = logging.getLogger(__name__)


class Shamrock:
    """API integration for Trefle service."""

    def __init__(self, token: str, page_size: Optional[int] = None) -> None:
        """Constructs the API object.

        The API wrapper will be configured to try requests 5 times with a backoff factor of 0.1. It
        will retry on errors 500, 502, 503 and 504 if anything is temporarily wrong with the
        service.

        :param token: A token string that is acquired from signup.
        :type token: str
        :param page_size: How many pages to return when calling an endpoint. If not specified, it
            will default to whatever the API has. Currently that's 30 items.
            (default is None)
        :type page_size: int
        """

        self.url: str = "https://v0.trefle.io/api/"
        self.headers: Dict[str, str] = {"Authorization": f"Bearer {token}"}
        self.page_size: Optional[int] = page_size
        self.result: Optional[requests.Response] = None
        self.session: requests.Session = requests.Session()
        retries: Retry = Retry(
            total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def __getattr__(self, attr: str) -> Callable[[Any, Any], Any]:
        """A dunder method to handle any calls to endpoints and navigation.

        It is easier to bundle endpoints this way since they share the common functionality. That
        includes the navigation.

        :param attr: An attribute that is going to get called. Either an endpoint or a navigation.
        :type attr: str
        :raises AttributeError if a passed attr is not specified in the ENDPOINTS or NAVIGATION.
        :returns: A callable if the attr is from a list of endpoints or navigation items.
        :rtype: callable
        """

        if attr in ENDPOINTS:

            def endpoint(*args: Any, **kwargs: Any) -> Callable[[Any, Any], Any]:
                return self.ENDPOINT(attr, *args, **kwargs)

            return endpoint
        elif attr in NAVIGATION:

            def navigate(*args: Any, **kwargs: Any) -> Callable[[Any, Any], Any]:
                return self.NAVIGATE(attr, *args, **kwargs)

            return navigate

        raise AttributeError

    def _get_full_url(self, endpoint: str) -> str:
        """Get a full URL that is constructed from a protocol, domain and API with an endpoint.

        It gets the predefined endpoint of the API from a instance variable and adds the endpoint.

        :param endpoint: An endpoint that will be added to the URL of the API.
        :type endpoint: str
        :returns: A string of the full URL.
        :rtype: str
        """

        return f"{self.url}{endpoint}"

    def _kwargs(self, endpoint: str, **query_parameters: Any) -> Dict[str, Any]:
        """Get a dict with string of keys and values that will eventually be passed to a request.

        A dict is constructed that is passed to the request when calling it. It contains URL and
        headers, and params, if any, to pass as a query string.

        :param endpoint: An endpoint that will be added to the URL of the API.
        :type endpoint: str
        :param **query_parameters: Any kwarg combination that will eventually end up as a query
            string.
        :type **query_parameters: Any
        :returns: A dict that will eventually get passed to the requests with strings as keys.
        :rtype: dict
        """

        kwargs: Dict[str, Any] = {
            "url": endpoint
            if endpoint.startswith("http")
            else self._get_full_url(endpoint),
            "headers": self.headers,
        }
        if self.page_size is not None:
            kwargs["params"] = {"page_size": self.page_size}
        if query_parameters:
            if "params" in kwargs:
                kwargs["params"].update(query_parameters)
            else:
                kwargs["params"] = query_parameters
        return kwargs

    def _get_parametrized_url(self, kwargs: Dict[str, Any]) -> str:
        """Get a URL with query string parameters.

        With passed kwargs dict, the URL value is added to a params value of it that is previously
        parsed through urllib parse function. If no params are set, it will just return a URL.

        :param kwargs: A dict that holds URL key and any optional params for it.
        :type kwargs: dict
        :returns: A str that holds a URL with query string parameters, if any.
        :rtype: str
        """

        try:
            params: str = parse.urlencode(kwargs["params"], quote_via=parse.quote_plus)
            return f"{kwargs['url']}?{params}"
        except KeyError:
            return kwargs["url"]

    def _get_result(self, kwargs: Dict[str, Any]) -> Any:
        """Get a response from a request object if it is not stored already in the class instance.

        If a response exists on the class instance and the URL is the same, it returns a JSON of the
        response. Otherwise it tries to get a response via a request call and logs any exceptions
        that may happen during the call. After the call is complete, it checks the status code and
        logs an error if it happens. Otherwise it will try to decode the response body as a JSON and
        return it with saving the response on the instance. Failing that, it will log an error and
        return None.

        :param kwargs: A dict that holds options for a request that will eventually be made.
        :type kwargs: dict
        :raises Timeout if the request times out.
        :raises TooManyRedirects if the request has too many redirects to follow.
        :raises ValueError if the resulting JSON response is invalid.
        :raises HTTPError if the response status code is bad.
        :returns: Any JSON that gets decoded from a successful response or None if it fails.
        :rtype: Any
        """

        if self.result is not None:
            built_url: str = self._get_parametrized_url(kwargs)
            if built_url == self.result.url:
                return self.result.json()
        try:
            response: requests.Response = self.session.get(**kwargs)
        except Timeout:
            logger.error("The request timed out.")
            raise
        except TooManyRedirects:
            logger.error("The request had too many redirects.")
            raise
        finally:
            self.session.close()

        try:
            response.raise_for_status()
            try:
                response_json: Any = response.json()
            except ValueError:
                logger.error("Invalid JSON in response.")
                raise
            else:
                self.result = response
                return response_json
        except HTTPError as e:
            logger.error(f"Unknown exception raised: {repr(e)}")
            raise

    def search(self, q: str, **kwargs: Any) -> Any:
        """Search the species and return results of the API call.

        Searches the Trefle database of any matching species of plants and returns either successful
        results or None.

        :param q: A string that is used to search the species with.
        :type q: str
        :param kwargs: Any query strings to add to the search object.
        :type kwargs: dict
        :returns: Any JSON that gets decoded from a successful response or None if it fails.
        :rtype: Any
        """

        query_parameters = {"q": q}
        query_parameters.update(**kwargs)
        kwargs = self._kwargs("species", **query_parameters)
        return self._get_result(kwargs)

    def ENDPOINT(self, endpoint: str, pk: Optional[int] = None, **kwargs: Any) -> Any:
        """Query the endpoint of the Trefle API and return results.

        This method is called on any endpoint defined for the API. It can return any result from
        it or None if it doesn't succeed.

        :param endpoint: An endpoint where the library will make a request.
        :type endpoint: str
        :param pk: (optional) A primary key of the element.
        :type pk: int
        :param kwargs: Any query strings to add to the search object.
        :type kwargs: dict
        :returns: Any JSON that gets decoded from a successful response or None if it fails.
        :rtype: Any
        """

        requests_kwargs: Dict[str, Any] = self._kwargs(
            f"{endpoint}/{pk:d}" if pk else endpoint, **kwargs
        )
        return self._get_result(requests_kwargs)

    def NAVIGATE(self, navigation: str, **kwargs: Any) -> Any:
        """Navigate the API if any navigation exists on the results once the first call is made and
        stored on the instance.

        This method is called on any navigation defined for the API. It can return any result from
        it or None if it doesn't succeed.

        :param navigation: A navigation option where the library will make a request.
        :type navigation: str
        :param kwargs: Any query strings to add to the search object.
        :type kwargs: dict
        :returns: Any JSON that gets decoded from a successful response or None if it fails.
        :rtype: Any
        """

        if self.result is not None and navigation in self.result.links:
            requests_kwargs: Dict[str, Any] = self._kwargs(
                self.result.links[navigation]["url"], **kwargs
            )
            return self._get_result(requests_kwargs)
