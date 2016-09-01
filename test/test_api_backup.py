"""Backup test functions."""
import os
import json
import shutil
import tempfile
from unittest import TestCase

from companion import error
from companion.api import backup, util

from . import create_test_data, es_url


class TempfileTestCase(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


class TestSaveHit(TempfileTestCase):

    def test_save_hit(self):
        """It should save a hit as a JSON file."""
        hit = {
            '_id': 'abcd',
            '_index': 'myindex',
            '_type': 'mytype',
            '_source': {
                'myfield': 'myvalue'
            }
        }
        target = os.path.join(self.tmpdir,
                              'myindex_mytype/myindex_mytype_abcd.json')

        saved_target = backup._save_hit(self.tmpdir, hit)
        self.assertEqual(saved_target, target)
        self.assertTrue(os.path.exists(target))
        with open(target) as f:
            hit_loaded = json.loads(f.read())
            self.assertEqual(hit, hit_loaded)


class TestFetchAndZip(TempfileTestCase):

    def test_not_exists(self):
        """It should not crash on indexes that do not exist."""
        tmpdir, zipfiles = backup._fetch_and_zip(es_url,
                                                 'fooindexname')
        self.assertIsNone(tmpdir)
        self.assertIsNone(zipfiles)

    def test_non_empty(self):
        """It should create zip-files by default."""
        create_test_data()
        tmpdir, zipfiles = backup._fetch_and_zip(es_url,
                                                 'companiontest')
        self.assertEqual(len(zipfiles), 2)
        zip1 = os.path.join(tmpdir, 'companiontest_simple.zip')
        zip2 = os.path.join(tmpdir, 'companiontest_advanced.zip')
        self.assertIn(zip1, zipfiles)
        self.assertIn(zip2, zipfiles)

    def test_non_empty(self):
        """It should create zip-files by default."""
        create_test_data()
        tmpdir, zipfiles = backup._fetch_and_zip(es_url,
                                                 'companiontest')
        self.assertEqual(len(zipfiles), 2)
        zip1 = os.path.join(tmpdir, 'companiontest_simple.zip')
        zip2 = os.path.join(tmpdir, 'companiontest_advanced.zip')
        self.assertIn(zip1, zipfiles)
        self.assertIn(zip2, zipfiles)

    def test_non_empty_small_batchsize(self):
        """It should create zip-files by default."""
        create_test_data()
        tmpdir, zipfiles = backup._fetch_and_zip(es_url,
                                                 'companiontest',
                                                 batch_size=1)
        self.assertEqual(len(zipfiles), 2)
        zip1 = os.path.join(tmpdir, 'companiontest_simple.zip')
        zip2 = os.path.join(tmpdir, 'companiontest_advanced.zip')
        self.assertIn(zip1, zipfiles)
        self.assertIn(zip2, zipfiles)


class TestFetchAndTar(TempfileTestCase):

    def test_not_exists(self):
        """It should not crash on indexes that do not exist."""
        tmpdir, tarfiles = backup._fetch_and_tar(es_url,
                                                 'fooindexname')
        self.assertIsNone(tmpdir)
        self.assertIsNone(tarfiles)

    def test_non_empty(self):
        """It should create zip-files by default."""
        create_test_data()
        tmpdir, tarfiles = backup._fetch_and_tar(es_url,
                                                 'companiontest')
        self.assertEqual(len(tarfiles), 2)
        tar1 = os.path.join(tmpdir, 'companiontest_simple.tar.gz')
        tar2 = os.path.join(tmpdir, 'companiontest_advanced.tar.gz')
        self.assertIn(tar1, tarfiles)
        self.assertIn(tar2, tarfiles)
