import json
import os
import unittest

import vcr as main_vcr
from shamrock import ENDPOINTS, Shamrock

TOKEN = os.environ.get("TREFLE_TOKEN")

vcr = main_vcr.VCR(
    cassette_library_dir="tests/cassettes", filter_headers=[("Authorization", None)]
)


class BasicTests(unittest.TestCase):
    def setUp(self):
        self.api = Shamrock(TOKEN)

    def tearDown(self):
        pass

    def assertCommon(self, response, result, name):
        self.assertEqual(len(response), 1)
        self.assertEqual(response.requests[0].uri, f"https://trefle.io/api/{name}")
        self.assertTrue(isinstance(result, list))
        self.assertEqual(result, json.loads(response.responses[0]["body"]["string"]))

    def test__get_full_url(self):
        url = self.api._get_full_url("species")
        self.assertEqual(url, "https://trefle.io/api/species")

    def test__kwargs(self):
        kwargs = self.api._kwargs("species")
        expected = {
            "url": "https://trefle.io/api/species",
            "headers": {"Authorization": f"Bearer {TOKEN}"},
        }
        self.assertEqual(kwargs, expected)
        kwargs = self.api._kwargs("https://example.com")
        expected = {
            "url": "https://example.com",
            "headers": {"Authorization": f"Bearer {TOKEN}"},
        }
        self.assertEqual(kwargs, expected)

    def test__get_parametrized_url(self):
        kwargs = {"url": "https://example.com/"}
        result = self.api._get_parametrized_url(kwargs)
        self.assertEqual(result, kwargs["url"])
        kwargs["params"] = {"q": "tomato"}
        result = self.api._get_parametrized_url(kwargs)
        self.assertEqual(result, f"{kwargs['url']}?q=tomato")

    def test__get_result(self):
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

    def test_ENDPOINTS(self):
        self.assertEqual(
            ENDPOINTS,
            (
                "kingdoms",
                "subkingdoms",
                "divisions",
                "families",
                "genuses",
                "plants",
                "species",
            ),
        )

    def test_invalid_endpoint(self):
        invalid_endpoint = "invalid_endpoint"
        self.assertTrue(invalid_endpoint not in ENDPOINTS)
        with self.assertRaises(AttributeError):
            getattr(self.api, invalid_endpoint)()

    def test_valid_endpoints(self):
        for endpoint in ENDPOINTS:
            with vcr.use_cassette(f"{endpoint}.yaml") as response:
                result = getattr(self.api, endpoint)()
                self.assertCommon(response, result, endpoint)

    def test_valid_endpoint_one(self):
        with vcr.use_cassette("species_one.yaml") as response:
            result = self.api.species(182512)
            self.assertEqual(len(response), 1)
            self.assertEqual(
                response.requests[0].uri, "https://trefle.io/api/species/182512"
            )
            self.assertTrue(isinstance(result, dict))
            self.assertEqual(
                result, json.loads(response.responses[0]["body"]["string"])
            )

    def test_search(self):
        with vcr.use_cassette("search.yaml") as response:
            result = self.api.search("tomato")
            self.assertEqual(len(response), 1)
            self.assertEqual(
                response.requests[0].uri, "https://trefle.io/api/species?q=tomato"
            )
            self.assertTrue(isinstance(result, list))
            self.assertEqual(
                result, json.loads(response.responses[0]["body"]["string"])
            )

    def test_next(self):
        with vcr.use_cassette("species.yaml"):
            self.api.species()
            self.assertIsNone(self.api.prev())
        with vcr.use_cassette("next.yaml") as response:
            result = self.api.next()
            self.assertTrue(isinstance(result, list))
            self.assertEqual(
                response.requests[0].uri, "http://trefle.io/api/species?page=2"
            )

    def test_prev(self):
        with vcr.use_cassette("species.yaml"):
            self.api.species()
        with vcr.use_cassette("next.yaml"):
            self.api.next()
        with vcr.use_cassette("prev.yaml") as response:
            result = self.api.prev()
            self.assertTrue(isinstance(result, list))
            self.assertEqual(
                response.requests[0].uri, "http://trefle.io/api/species?page=1"
            )
        with vcr.use_cassette("last.yaml") as response:
            self.api.last()
            self.assertIsNone(self.api.next())

    def test_first(self):
        with vcr.use_cassette("species.yaml"):
            self.api.species()
        with vcr.use_cassette("first.yaml"):
            self.assertIsNotNone(self.api.first())

    def test_last(self):
        with vcr.use_cassette("species.yaml"):
            self.api.species()
        with vcr.use_cassette("last.yaml"):
            self.assertIsNotNone(self.api.last())
            self.assertIsNone(self.api.next())

    def test_config(self):
        self.api = Shamrock(TOKEN, page_size=30)
        with vcr.use_cassette("species_config.yaml") as response:
            result = self.api.species()
            self.assertEqual(len(response), 1)
            self.assertEqual(
                response.requests[0].uri, "https://trefle.io/api/species?page_size=30"
            )
            self.assertTrue(isinstance(result, list))
            self.assertEqual(
                result, json.loads(response.responses[0]["body"]["string"])
            )
        with vcr.use_cassette("search_config.yaml") as response:
            result = self.api.search("tomato")
            self.assertEqual(len(response), 1)
            self.assertEqual(
                response.requests[0].uri,
                "https://trefle.io/api/species?page_size=30&q=tomato",
            )
            self.assertTrue(isinstance(result, list))
            self.assertEqual(
                result, json.loads(response.responses[0]["body"]["string"])
            )
