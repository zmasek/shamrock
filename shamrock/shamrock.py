"""Shamrock - A Trefle API Integration."""
import copy
import logging
from typing import Any, Callable, Dict, Optional, Tuple, Union
from urllib import parse

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError, Timeout, TooManyRedirects
from requests.packages.urllib3.util.retry import Retry

from .decorators import _check_argument_value
from .exceptions import ShamrockException
from .messages import (
    EXCEPTION_JSON,
    EXCEPTION_REDIRECTS,
    EXCEPTION_TIMEOUT,
    EXCEPTION_UNKNOWN,
    INSTANCE,
)

ENDPOINTS: Tuple[str, ...] = (
    "kingdoms",
    "subkingdoms",
    "divisions",
    "division_classes",
    "division_orders",
    "families",
    "genus",
    "plants",
    "species",
    "distributions",
)
NAVIGATION: Tuple[str, ...] = ("next", "prev", "first", "last")
BASE_URL: str = "https://trefle.io/"

logger: logging.Logger = logging.getLogger(__name__)


class Shamrock:
    """API integration for Trefle service."""

    def __init__(self, token: str) -> None:
        """Constructs the API object.

        The API wrapper will be configured to try requests 5 times with a backoff factor of 0.1. It
        will retry on errors 500, 502, 503 and 504 if anything is temporarily wrong with the
        service.

        :param token: A token string that is acquired from the personal profile settings.
        :type token: str
        """

        self.token: str = token
        self.version: str = "v1"  # This should become a parameter when the Trefle API changes
        self.base_url: str = BASE_URL
        self.api_url: str = f"{self.base_url}api/"
        self.api_version_url: str = f"{self.api_url}{self.version}/"
        self.default_query_parameters: Dict[str, Any] = {"token": token}
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

        return (
            f"{self.base_url}{endpoint[1:]}"
            if endpoint.startswith("/")
            else f"{self.api_version_url}{endpoint}"
        )

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
            else self._get_full_url(endpoint)
        }
        kwargs["params"] = copy.deepcopy(self.default_query_parameters)
        if query_parameters:
            kwargs["params"].update(query_parameters)
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

    @_check_argument_value("method", ("GET", "POST"))
    def _get_result(
        self, kwargs: Dict[str, Any], method: str = "GET", json: Optional[Any] = None
    ) -> Any:
        """Get a response from a request object if it is not stored already in the class instance.

        If a response exists on the class instance and the URL is the same, it returns a JSON of the
        response. Otherwise it tries to get a response via a request call and logs any exceptions
        that may happen during the call. After the call is complete, it checks the status code and
        logs an error if it happens. Otherwise it will try to decode the response body as a JSON and
        return it with saving the response on the instance. Failing that, it will log an error and
        raise it.

        :param kwargs: A dict that holds options for a request that will eventually be made.
        :type kwargs: dict
        :param method: A string specifying the HTTP method, either "GET" by default or "POST".
        :type method: str
        :param json: Any object that can get serialized as a JSON when submitted to an endpoint.
        :type json: (optional) most often a dict that gets submitted as a JSON body.
        :raises ShamrockException if the request method is illegal or the request throws an
            exception or the response is bad.
        :returns: Any JSON that gets decoded from a successful response or None if it fails.
        :rtype: Any
        """

        if self.result is not None:
            built_url: str = self._get_parametrized_url(kwargs)
            if built_url == self.result.url:
                return self.result.json()
        try:
            response: requests.Response = self.session.get(
                **kwargs
            ) if method == "GET" else self.session.post(json=json, **kwargs)
        except Timeout:
            logger.error(EXCEPTION_TIMEOUT)
            raise ShamrockException(EXCEPTION_TIMEOUT)
        except TooManyRedirects:
            logger.error(EXCEPTION_REDIRECTS)
            raise ShamrockException(EXCEPTION_REDIRECTS)
        finally:
            self.session.close()

        try:
            response.raise_for_status()
            try:
                response_json: Any = response.json()
            except ValueError:
                logger.error(EXCEPTION_JSON)
                raise ShamrockException(EXCEPTION_JSON)
            else:
                self.result = response
                return response_json
        except HTTPError as e:
            message = EXCEPTION_UNKNOWN.format(exception=repr(e))
            logger.error(message)
            raise ShamrockException(message)

    @_check_argument_value("what", ("plants", "species"))
    def search(self, q: str, what: str = "plants", **kwargs: Any) -> Any:
        """Search the plant and return results of the API call.

        Searches the Trefle database of any matching plant and return either a successful result or
        None.

        :param q: A string that is used to search the plant with.
        :type q: str
        :param what: A string that is signifying what item to report an error on.
        :type what: str (if not specified, then "plants", but can be specified as "species")
        :param **kwargs: Any query strings to add to the search object.
        :type **kwargs: dict
        :raises ShamrockException if the type of query is illegal.
        :returns: Any JSON that gets decoded from a successful response.
        :rtype: Any
        """

        query_parameters: Dict[str, Any] = {"q": q}
        query_parameters.update(kwargs)
        request_kwargs: Dict[str, Any] = self._kwargs(
            f"{what}/search", **query_parameters
        )
        return self._get_result(request_kwargs)

    @_check_argument_value("what", ("plants", "species"))
    def report_error(
        self,
        identifier: Union[int, str],
        notes: str,
        what: str = "plants",
        **kwargs: Any,
    ) -> Any:
        """Report an error in the API database by passing the notes. The error can be reported to
        either the plants or the species. By default, to plants, providing an identifier of an item.

        Returns the response of a report.

        :param identifier: An identifier, either a slug or a primary key of the entry.
        :type identifier: int or str
        :param notes: A string that is delivered to report an error on the entry.
        :type notes: str
        :param what: A string that is signifying what item to report an error on.
        :type what: str (if not specified, then "plants", but can be specified as "species")
        :param kwargs: Any query strings to add to the post object.
        :type kwargs: dict
        :raises ShamrockException if the type of report is illegal.
        :returns: Any JSON that gets decoded from a successful response.
        :rtype: Any
        """

        json: Dict[str, str] = {"notes": notes}
        request_kwargs: Dict[str, Any] = self._kwargs(f"{what}/{identifier}/report")
        return self._get_result(request_kwargs, method="POST", json=json)

    @_check_argument_value("modifier", ("distributions", "genus"))
    def plants_by(
        self, modifier: str, identifier: Union[int, str], **kwargs: Any
    ) -> Any:
        """Returns all the plants in a given distribution or genus.

        :param modifier: A string that tells what to use as a lookup. Either "distributions" or
            "genus".
        :type modifier: str
        :param identifier: An identifier, either a slug or a primary key of the modifier.
        :type identifier: int or str
        :param **kwargs: Any query string options to add to the call.
        :type **kwargs: dict
        :raises ShamrockException if the value of modifier is wrong.
        :returns: Any JSON that gets decoded from a successful response.
        :rtype: Any
        """

        request_kwargs: Dict[str, Any] = self._kwargs(
            f"{modifier}/{identifier}/plants", **kwargs
        )
        return self._get_result(request_kwargs)

    def corrections(
        self,
        identifier: Optional[Union[int, str]] = None,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> Any:
        """Returns one correction or a list of corrections, or submits one.

        :param identifier: An identifier, a primary key of the correction.
        :type identifier: int
        :param json: Any object that can get serialized as a JSON when submitted to an endpoint.
        :type json: (optional) most often a dict that gets submitted as a JSON body.
        :param **kwargs: Any query string options to add to the call.
        :type **kwargs: dict
        :returns: Any JSON that gets decoded from a successful response.
        :rtype: Any
        """
        request_kwargs: Dict[str, Any] = {}
        if json is None:
            request_kwargs = self._kwargs(
                f"corrections/{identifier}" if identifier else "corrections", **kwargs
            )
            return self._get_result(request_kwargs)
        else:
            request_kwargs = self._kwargs(f"corrections/species/{identifier}", **kwargs)
            return self._get_result(request_kwargs, method="POST", json=json)

    def auth(self, origin: str, **kwargs: Any) -> Any:
        """Returns a JWT that you can use in a browser. You need to specify where you'll be using
        the token so it can be bound to a certain address.

        :param origin: A URL that is delivered to the endpoint so the responding JWT can use it.
        :type origin: str
        :param **kwargs: Any query string options to add to the call.
        :type **kwargs: dict
        """
        query_parameters: Dict[str, Any] = {"origin": origin}
        query_parameters.update(kwargs)
        request_kwargs: Dict[str, Any] = self._kwargs(
            f"/api/auth/claim", **query_parameters
        )
        return self._get_result(request_kwargs, method="POST")

    def ENDPOINT(
        self, endpoint: str, identifier: Optional[Union[int, str]] = None, **kwargs: Any
    ) -> Any:
        """Query the endpoint of the Trefle API and return results.

        This method is called on any endpoint defined for the API. It can return any result from
        it or None if it doesn't succeed.

        :param endpoint: An endpoint where the library will make a request.
        :type endpoint: str
        :param identifier: (optional) A primary key or the slug of the element.
        :type identifier: int, str
        :param **kwargs: Any query strings to add to the search object.
        :type **kwargs: dict
        :returns: Any JSON that gets decoded from a successful response or None if it fails.
        :rtype: Any
        """

        request_kwargs: Dict[str, Any] = self._kwargs(
            f"{endpoint}/{identifier}" if identifier else endpoint, **kwargs
        )
        return self._get_result(request_kwargs)

    def NAVIGATE(self, navigation: str, **kwargs: Any) -> Any:
        """Navigate the API if any navigation exists on the results once the first call is made and
        stored on the instance.

        This method is called on any navigation defined for the API. It can return any result from
        it or None if it doesn't succeed.

        :param navigation: A navigation option where the library will make a request.
        :type navigation: str
        :param **kwargs: Any query strings to add to the search object.
        :type **kwargs: dict
        :returns: Any JSON that gets decoded from a successful response or None if it fails.
        :rtype: Any
        """

        if self.result is not None and navigation in self.result.json().get("links"):
            request_kwargs: Dict[str, Any] = self._kwargs(
                self.result.json()["links"][navigation], **kwargs
            )
            return self._get_result(request_kwargs)

    def __str__(self) -> str:
        """Describe the Shamrock instance."""
        return INSTANCE.format(token=self.token, version=self.version)
