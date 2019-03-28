from urllib import parse

import requests
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


class Shamrock:
    def __init__(self, token: str, page_size: Optional[int] = None) -> None:
        self.url: str = "https://trefle.io/api/"
        self.headers: Dict[str, str] = {"Authorization": "Bearer {}".format(token)}
        self.page_size: Optional[int] = page_size
        self.result: Optional[requests.Response] = None

    def __getattr__(self, attr: str) -> Callable[[Any, Any], Any]:
        if attr in ENDPOINTS:

            def wrapper(*args: Any, **kwargs: Any) -> Callable[[Any, Any], Any]:
                return self.ENDPOINT(attr, *args, **kwargs)

            return wrapper
        raise AttributeError

    def _get_full_url(self, endpoint: str) -> str:
        return "{}{}".format(self.url, endpoint)

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
            return "{}?{}".format(kwargs["url"], params)
        except KeyError:
            return kwargs["url"]

    def _get_result(self, kwargs: Dict[str, Any]) -> Any:
        if self.result is not None:
            built_url = self._get_parametrized_url(kwargs)
            if built_url == self.result.url:
                return self.result.json()
        self.result = requests.get(**kwargs)
        return self.result.json()

    def search(self, q: str, **kwargs: Any) -> Any:
        query_parameters = {"q": q}
        query_parameters.update(dict(**kwargs))
        kwargs = self._kwargs("species", **query_parameters)
        return self._get_result(kwargs)

    def ENDPOINT(self, endpoint: str, pk: Optional[int] = None, **kwargs: Any) -> Any:
        kwargs = self._kwargs("{}/{:d}".format(endpoint, pk) if pk else endpoint)
        return self._get_result(kwargs)

    def next(self) -> Any:
        if self.result is not None and "next" in self.result.links:
            kwargs: Dict[str, Any] = self._kwargs(self.result.links["next"]["url"])
            self.result: requests.Response = requests.get(**kwargs)
            return self.result.json()

    def previous(self) -> Any:
        if self.result is not None and "prev" in self.result.links:
            kwargs: Dict[str, Any] = self._kwargs(self.result.links["prev"]["url"])
            self.result: requests.Response = requests.get(**kwargs)
            return self.result.json()

    def first(self) -> Any:
        if self.result is not None and "first" in self.result.links:
            kwargs: Dict[str, Any] = self._kwargs(self.result.links["first"]["url"])
            self.result: requests.Response = requests.get(**kwargs)
            return self.result.json()

    def last(self) -> Any:
        if self.result is not None and "last" in self.result.links:
            kwargs: Dict[str, Any] = self._kwargs(self.result.links["last"]["url"])
            self.result: requests.Response = requests.get(**kwargs)
            return self.result.json()
