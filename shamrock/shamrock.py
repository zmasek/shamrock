import logging
from urllib import parse

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError, Timeout, TooManyRedirects
from requests.packages.urllib3.util.retry import Retry
from typing import Any, Callable, Dict, Optional, Tuple

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
    def __init__(self, token: str, page_size: Optional[int] = None) -> None:
        self.url: str = "https://trefle.io/api/"
        self.headers: Dict[str, str] = {"Authorization": f"Bearer {token}"}
        self.page_size: Optional[int] = page_size
        self.result: Optional[requests.Response] = None
        self.session: requests.Session = requests.Session()
        retries: Retry = Retry(
            total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def __getattr__(self, attr: str) -> Callable[[Any, Any], Any]:
        if attr in ENDPOINTS:

            def endpoint(*args: Any, **kwargs: Any) -> Callable[[Any, Any], Any]:
                return self.ENDPOINT(attr, *args, **kwargs)

            return endpoint
        elif attr in NAVIGATION:

            def navigate(*args, **kwargs) -> Callable[[Any, Any], Any]:
                return self.NAVIGATE(attr, *args, **kwargs)

            return navigate

        raise AttributeError

    def _get_full_url(self, endpoint: str) -> str:
        return f"{self.url}{endpoint}"

    def _kwargs(self, endpoint: str, **query_parameters: Any) -> Dict[str, Any]:
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
                kwargs["params"].update(dict(**query_parameters))
            else:
                kwargs["params"] = dict(**query_parameters)
        return kwargs

    def _get_parametrized_url(self, kwargs: Dict[str, Any]) -> str:
        try:
            params: str = parse.urlencode(kwargs["params"], quote_via=parse.quote_plus)
            return f"{kwargs['url']}?{params}"
        except KeyError:
            return kwargs["url"]

    def _get_result(self, kwargs: Dict[str, Any]) -> Any:
        if self.result is not None:
            built_url: str = self._get_parametrized_url(kwargs)
            if built_url == self.result.url:
                return self.result.json()
        try:
            response: requests.Response = self.session.get(**kwargs)
        except Timeout:
            logger.error("The request timed out.")
        except TooManyRedirects:
            logger.error("The request had too many redirects.")

        try:
            response.raise_for_status()
            try:
                response_json: Any = response.json()
            except ValueError:
                logger.error("Invalid JSON in response.")
            else:
                self.session.close()
                self.result = response
                return response_json
        except HTTPError as e:
            logger.error("Unknown exception raised: ", e)

    def search(self, q: str, **kwargs: Any) -> Any:
        query_parameters = {"q": q}
        query_parameters.update(dict(**kwargs))
        kwargs = self._kwargs("species", **query_parameters)
        return self._get_result(kwargs)

    def ENDPOINT(self, endpoint: str, pk: Optional[int] = None, **kwargs: Any) -> Any:
        requests_kwargs: Dict[str, Any] = self._kwargs(
            f"{endpoint}/{pk:d}" if pk else endpoint
        )
        return self._get_result(requests_kwargs)

    def NAVIGATE(self, navigation: str, *args: Any, **kwargs: Any) -> Any:
        if self.result is not None and navigation in self.result.links:
            requests_kwargs: Dict[str, Any] = self._kwargs(
                self.result.links[navigation]["url"]
            )
            return self._get_result(requests_kwargs)
