"""Setup test functions."""
from unittest import TestCase

from companion import error
from companion.api import setup as api_setup

from . import es_url


class TestIndexMapper(TestCase):
    def test_init(self):
        """It should create an IndexMapper with a correct directory"""
        im = api_setup.IndexMapper(es_url, data_path='./companion')
        self.assertIsNotNone(im)

    def test_data_dir_error(self):
        """It should raise an exception if a directory does not exist."""
        with self.assertRaises(error.CompanionException):
            api_setup.IndexMapper(es_url, data_path='./hejhej')
