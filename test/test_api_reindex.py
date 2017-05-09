"""Reindex test functions."""
from unittest import TestCase

from companion.api import reindex, util

from . import create_test_data, es_url


class TestDateReindex(TestCase):

    def setUp(self):
        self.client = util.get_client(es_url)
        self.client.indices.delete(index='companiontesttarget*', ignore=[404])

    def test_empty_arguments(self):
        """It should require url, index and doc type."""
        with self.assertRaises(Exception):
            reindex.date_reindex()

    def test_empty_query(self):
        """It should reindex all documents"""
        create_test_data()
        reindex.date_reindex(es_url,
                             'companiontest',
                             'companiontesttarget')

        # Remember to refresh
        self.client.indices.refresh(index='companiontesttarget')

        cnt = self.client.count(index='companiontesttarget')
        self.assertEqual(cnt['count'], 4)

        # Using the same IDs as before.
        exists = self.client.exists(index='companiontesttarget',
                                    doc_type='simple',
                                    id='foo')
        self.assertTrue(exists)

    def test_new_ids(self):
        """It should create new IDs if specified"""
        create_test_data()
        reindex.date_reindex(es_url,
                             'companiontest',
                             'companiontesttarget',
                             use_same_id=False)

        # Remember to refresh
        self.client.indices.refresh(index='companiontesttarget')

        cnt = self.client.count(index='companiontesttarget')
        self.assertEqual(cnt['count'], 4)

        # Using the same IDs as before.
        exists = self.client.exists(index='companiontesttarget',
                                    doc_type='simple',
                                    id='foo')
        self.assertFalse(exists)

    def test_temporal_date(self):
        """It should use a date field for index naming"""
        create_test_data()
        reindex.date_reindex(es_url,
                             'companiontest',
                             'companiontesttarget-{:%Y-%m-%d}',
                             date_field='timestamp')

        # Remember to refresh
        self.client.indices.refresh(index='companiontesttarget*')

        cnt = self.client.count(index='companiontesttarget-2015-01-01')
        self.assertEqual(cnt['count'], 2)

        cnt = self.client.count(index='companiontesttarget-2015-01-02')
        self.assertEqual(cnt['count'], 1)

        cnt = self.client.count(index='companiontesttarget-2015-01-03')
        self.assertEqual(cnt['count'], 1)

    def test_with_query(self):
        """It should use a query"""
        create_test_data()

        # Re-index documents created after 2015-01-01.
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
        reindex.date_reindex(es_url,
                             'companiontest',
                             'companiontesttarget',
                             query=query)

        # Remember to refresh
        self.client.indices.refresh(index='companiontesttarget')

        cnt = self.client.count(index='companiontesttarget')
        self.assertEqual(cnt['count'], 2)

    def test_scan_kwargs(self):
        """It should use the scanner arguments"""
        create_test_data()

        scan_kwargs = {
            'doc_type': 'advanced'
        }

        reindex.date_reindex(es_url,
                             'companiontest',
                             'companiontesttarget',
                             scan_kwargs=scan_kwargs)

        # Remember to refresh
        self.client.indices.refresh(index='companiontesttarget')

        cnt = self.client.count(index='companiontesttarget')
        self.assertEqual(cnt['count'], 1)
