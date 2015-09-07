"""Util test functions."""
import os
import shutil
import tarfile
import tempfile
from unittest import TestCase

from elasticsearch import Elasticsearch

from companion.api import util


class TestPretty(TestCase):
    def test_pretty_basic(self):
        """It should return an empty JSON string for an empty dict."""
        d = {}
        s = util.pretty(d)
        self.assertEqual(s, '{}')

    def test_pretty_multiline(self):
        """It should return a multiline JSON string for a dict with members."""
        d = {'a': 1}
        s = util.pretty(d)
        self.assertEqual(s, '{\n  "a": 1\n}')


class TestGetClient(TestCase):
    def test_get_client(self):
        """It should return an Elasticsearch client."""
        client = util.get_client('http://localhost:9200')
        self.assertIsInstance(client, Elasticsearch)


class TestTarGzDirectory(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_tar_gz(self):
        """It should compress a file and be able to decompress."""
        compressdir = os.path.join(self.tmpdir, 'test/')
        checkdir = os.path.join(self.tmpdir, 'check/')
        os.mkdir(compressdir)
        os.mkdir(checkdir)
        filename = os.path.join(compressdir, 'testfile.txt')
        check_filename = os.path.join(checkdir, 'test/testfile.txt')
        with open(filename, 'w') as f:
            f.write('This string will be compressed')
        tar_path = util.tar_gz_directory(compressdir, self.tmpdir)

        # Tar file should be smaller
        self.assertLess(os.path.getsize(filename), os.path.getsize(tar_path))

        # Tar file should be able to decompress and have same contents as
        # before.
        with tarfile.open(tar_path) as f:
            f.extractall(checkdir)

        with open(check_filename) as f:
            s = f.read()
            self.assertEqual(s, 'This string will be compressed')
