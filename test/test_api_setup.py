"""Util test functions."""
from unittest import TestCase

from companion import error
from companion.api import setup as api_setup


class TestIndexMapper(TestCase):
    def test_init(self):
        """It should create an IndexMapper with a correct directory"""
        im = api_setup.IndexMapper('http://localhost:9200',
                                   data_path='./companion')
        self.assertIsNotNone(im)

    def test_data_dir_error(self):
        """It should raise an exception if a directory does not exist."""
        with self.assertRaises(error.CompanionException):
            api_setup.IndexMapper('http://localhost:9200',
                                  data_path='./hejhej')
