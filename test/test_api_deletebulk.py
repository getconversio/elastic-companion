"""Bulk delete test functions."""
from unittest import TestCase

from companion.api import deletebulk, util

from . import create_test_data, es_url


class TestDeleteByQuery(TestCase):

    def setUp(self):
        self.client = util.get_client(es_url)

    def test_empty_arguments(self):
        """It should require url, index and doc type."""
        with self.assertRaises(Exception):
            deletebulk.delete_by_query()

    def test_empty_query(self):
        """It should allow an empty query"""
        create_test_data()
        deletebulk.delete_by_query(es_url,
                                   'companiontest',
                                   'simple',
                                   None)

        # Remember to refresh
        self.client.indices.refresh(index='companiontest')

        cnt = self.client.count(index='companiontest', doc_type='simple')
        self.assertEqual(cnt['count'], 0)

    def test_ensure_specific_doc_type(self):
        """It should only delete the given doc type"""
        create_test_data()
        deletebulk.delete_by_query(es_url,
                                   'companiontest',
                                   'simple',
                                   None)

        # Remember to refresh
        self.client.indices.refresh(index='companiontest')

        cnt = self.client.count(index='companiontest', doc_type='simple')
        self.assertEqual(cnt['count'], 0)

        cnt = self.client.count(index='companiontest', doc_type='advanced')
        self.assertEqual(cnt['count'], 1)

    def test_with_query(self):
        """It should use a given query"""
        create_test_data()

        # Deletes everything after 1/1
        query = {
            "query": {
                "bool": {
                    "filter": {
                        "range": {
                            "timestamp": {
                                "gte": "2015-01-02"
                            }
                        }
                    }
                }
            }
        }
        deletebulk.delete_by_query(es_url,
                                   'companiontest',
                                   'simple',
                                   query)

        # Remember to refresh
        self.client.indices.refresh(index='companiontest')

        cnt = self.client.count(index='companiontest', doc_type='simple')
        self.assertEqual(cnt['count'], 1)
