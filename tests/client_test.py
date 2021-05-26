import os
import unittest
from reversemx import Client
from reversemx import ParameterError, ApiAuthError


class TestClient(unittest.TestCase):
    """
    Final integration tests without mocks.

    Active API_KEY is required.
    """
    def setUp(self) -> None:
        self.client = Client(os.getenv('API_KEY'))

    def test_get_correct_data(self):
        response = self.client.data("aspmx.l.google.com")
        self.assertIsNotNone(response.size)

    def test_extra_parameters(self):
        response = self.client.data(
            "aspmx.l.google.com",
            search_from="0"
        )
        self.assertIsNotNone(response.size)

    def test_empty_terms(self):
        with self.assertRaises(ParameterError):
            self.client.data("")

    def test_getting_next_page(self):
        resp = self.client.data("aspmx.l.google.com")
        if resp.has_next():
            next_page = self.client.next_page("aspmx.l.google.com", resp)
            self.assertIsNotNone(next_page.current_page)

    def test_iterating(self):
        limit = 3
        for page in self.client.iterate_pages("aspmx.l.google.com"):
            self.assertIsNotNone(page.size)
            limit -= 1
            if limit <= 0:
                break

    def test_incorrect_api_key(self):
        client = Client('at_00000000000000000000000000000')
        with self.assertRaises(ApiAuthError):
            client.data("aspmx.l.google.com")

    def test_raw_data(self):
        response = self.client.raw_data(
            "aspmx.l.google.com",
            response_format=Client.XML_FORMAT)
        self.assertTrue(response.startswith('<?xml'))


if __name__ == '__main__':
    unittest.main()
