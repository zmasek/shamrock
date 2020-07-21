# -*- coding: utf-8 -*-

"""Tests for `Shamrock` package."""
import gzip
import json
import os
import unittest
from unittest.mock import patch

import vcr as main_vcr
from requests.exceptions import HTTPError, Timeout, TooManyRedirects

import shamrock
from shamrock import ENDPOINTS, NAVIGATION, Shamrock
from shamrock.exceptions import ShamrockException

TOKEN = os.environ.get("TREFLE_TOKEN")

vcr = main_vcr.VCR(
    cassette_library_dir="tests/cassettes", filter_query_parameters=["token"]
)


class BasicTests(unittest.TestCase):
    """Tests for `Shamrock` package."""

    def setUp(self):
        """Set up test API."""
        self.api = Shamrock(TOKEN)

    def tearDown(self):
        """Tear down test setup."""

    def assertCommon(self, response, result, name):
        """Assert common values."""
        self.assertEqual(len(response), 1)
        self.assertEqual(response.requests[0].uri, f"https://trefle.io/api/v1/{name}")
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(
            result, json.loads(gzip.decompress(response.responses[0]["body"]["string"]))
        )

    def test__get_full_url(self):
        """Test _get_full_url."""
        url = self.api._get_full_url("species")
        self.assertEqual(url, "https://trefle.io/api/v1/species")

    def test__kwargs(self):
        """Test _kwargs."""
        kwargs = self.api._kwargs("species")
        expected = {
            "url": "https://trefle.io/api/v1/species",
            "params": {"token": TOKEN},
        }
        self.assertEqual(kwargs, expected)
        kwargs = self.api._kwargs("https://example.com")
        expected = {"url": "https://example.com", "params": {"token": TOKEN}}
        self.assertEqual(kwargs, expected)

    def test__get_parametrized_url(self):
        """Test _get_parametrized_url."""
        kwargs = {"url": "https://example.com/"}
        result = self.api._get_parametrized_url(kwargs)
        self.assertEqual(result, kwargs["url"])
        kwargs["params"] = {"q": "tomato"}
        result = self.api._get_parametrized_url(kwargs)
        self.assertEqual(result, f"{kwargs['url']}?q=tomato")

    def test__get_result(self):
        """Test _get_result."""
        self.api.result = None
        kwargs = self.api._kwargs("species")
        with vcr.use_cassette("species.yaml") as response:
            result = self.api._get_result(kwargs)
            self.assertCommon(response, result, "species")
        with vcr.use_cassette("species.yaml") as response:
            result = self.api._get_result(kwargs)
            self.assertCommon(response, result, "species")
        kwargs = self.api._kwargs("plants")
        with vcr.use_cassette("plants.yaml") as response:
            result = self.api._get_result(kwargs)
            self.assertCommon(response, result, "plants")
        with patch.object(self.api, "result", return_value=None):
            with patch.object(self.api.session, "get", side_effect=Timeout):
                with self.assertRaises(ShamrockException) as e:
                    result = self.api._get_result(kwargs)
                self.assertEqual("The request timed out.", str(e.exception))
            with patch.object(self.api.session, "get", side_effect=TooManyRedirects):
                with self.assertRaises(ShamrockException) as e:
                    result = self.api._get_result(kwargs)
                self.assertEqual(
                    "The request had too many redirects.", str(e.exception)
                )
            with patch.object(
                shamrock.shamrock.requests.Response, "json", side_effect=ValueError
            ):
                with self.assertRaises(ShamrockException) as e:
                    result = self.api._get_result(kwargs)
                self.assertEqual("Invalid JSON in response.", str(e.exception))
            with patch.object(
                shamrock.shamrock.requests.Response,
                "raise_for_status",
                side_effect=HTTPError,
            ):
                with self.assertRaises(ShamrockException) as e:
                    result = self.api._get_result(kwargs)
                self.assertTrue(
                    str(e.exception).startswith("Unknown exception raised:")
                )

    def test_ENDPOINTS(self):
        """Test ENDPOINTS."""
        self.assertEqual(
            ENDPOINTS,
            (
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
            ),
        )

    def test_NAVIGATION(self):
        """Test NAVIGATION."""
        self.assertEqual(NAVIGATION, ("next", "prev", "first", "last"))

    def test_invalid_endpoint(self):
        """Test invalid endpoint."""
        invalid_endpoint = "invalid_endpoint"
        self.assertTrue(invalid_endpoint not in ENDPOINTS)
        with self.assertRaises(AttributeError):
            getattr(self.api, invalid_endpoint)()

    def test_valid_endpoints(self):
        """Test all valid endpoints."""
        for endpoint in ENDPOINTS:
            with vcr.use_cassette(f"{endpoint}.yaml") as response:
                result = getattr(self.api, endpoint)()
                self.assertCommon(response, result, endpoint)

    def test_valid_endpoint_one(self):
        """Test valid endpoint with a primary key."""
        with vcr.use_cassette("species_one.yaml") as response:
            result = self.api.species(182512)
            self.assertEqual(len(response), 1)
            self.assertEqual(
                response.requests[0].uri, "https://trefle.io/api/v1/species/182512"
            )
            self.assertTrue(isinstance(result, dict))
            self.assertEqual(
                result,
                json.loads(gzip.decompress(response.responses[0]["body"]["string"])),
            )

    def test_search(self):
        """Test search of species."""
        with vcr.use_cassette("search.yaml") as response:
            result = self.api.search("tomato")
            self.assertEqual(len(response), 1)
            self.assertEqual(
                response.requests[0].uri,
                "https://trefle.io/api/v1/plants/search?q=tomato",
            )
            self.assertTrue(isinstance(result, dict))
            self.assertEqual(
                result,
                json.loads(gzip.decompress(response.responses[0]["body"]["string"])),
            )

    def test_query_parameters(self):
        """Test query parameters."""
        with vcr.use_cassette("query_parameter_example.yaml") as response:
            result = self.api.species(common_name="blackwood")
            self.assertEqual(len(response), 1)
            self.assertEqual(
                response.requests[0].uri,
                "https://trefle.io/api/v1/species?common_name=blackwood",
            )
            self.assertTrue(isinstance(result, dict))
            self.assertEqual(
                result,
                json.loads(gzip.decompress(response.responses[0]["body"]["string"])),
            )

    def test_next(self):
        """Test next in navigation."""
        with vcr.use_cassette("species.yaml"):
            self.api.species()
            self.assertIsNone(self.api.prev())
        with vcr.use_cassette("next.yaml") as response:
            result = self.api.next()
            self.assertTrue(isinstance(result, dict))
            self.assertEqual(
                response.requests[0].uri, "https://trefle.io/api/v1/species?page=2"
            )

    def test_prev(self):
        """Test prev in navigation."""
        with vcr.use_cassette("species.yaml"):
            self.api.species()
        with vcr.use_cassette("next.yaml"):
            self.api.next()
        with vcr.use_cassette("prev.yaml") as response:
            result = self.api.prev()
            self.assertTrue(isinstance(result, dict))
            self.assertEqual(
                response.requests[0].uri, "https://trefle.io/api/v1/species?page=1"
            )
        with vcr.use_cassette("last.yaml") as response:
            self.api.last()
            self.assertIsNone(self.api.next())

    def test_first(self):
        """Test first in navigation."""
        with vcr.use_cassette("species.yaml"):
            self.api.species()
        with vcr.use_cassette("first.yaml"):
            self.assertIsNotNone(self.api.first())

    def test_last(self):
        """Test last in navigation."""
        with vcr.use_cassette("species.yaml"):
            self.api.species()
        with vcr.use_cassette("last.yaml"):
            self.assertIsNotNone(self.api.last())
            self.assertIsNone(self.api.next())

    def test_config(self):
        """Test different configuration for API integration."""
        self.api = Shamrock(TOKEN)
        with vcr.use_cassette("species_config.yaml") as response:
            result = self.api.species()
            self.assertEqual(len(response), 1)
            self.assertEqual(
                response.requests[0].uri, "https://trefle.io/api/v1/species"
            )
            self.assertTrue(isinstance(result, dict))
            self.assertEqual(
                result,
                json.loads(gzip.decompress(response.responses[0]["body"]["string"])),
            )
        with vcr.use_cassette("search_config.yaml") as response:
            result = self.api.search("tomato")
            self.assertEqual(len(response), 1)
            self.assertEqual(
                response.requests[0].uri,
                "https://trefle.io/api/v1/plants/search?q=tomato",
            )
            self.assertTrue(isinstance(result, dict))
            self.assertEqual(
                result,
                json.loads(gzip.decompress(response.responses[0]["body"]["string"])),
            )
