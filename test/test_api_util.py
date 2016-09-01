"""Util test functions."""
import os
import uuid
import shutil
import tarfile
import zipfile
import tempfile
from unittest import TestCase

from elasticsearch import Elasticsearch

from companion.api import util

from . import es_url


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
        client = util.get_client(es_url)
        self.assertIsInstance(client, Elasticsearch)
        self.assertTrue(client.transport.retry_on_timeout)


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


class TestZipDirectory(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.compressdir = os.path.join(self.tmpdir, 'test/')
        os.mkdir(self.compressdir)
        self.create_file()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def create_file(self, filename=None):
        if filename:
            self.filename = filename
        else:
            self.filename = '{}.txt'.format(uuid.uuid4())
        self.filepath = os.path.join(self.compressdir, self.filename)

        # If the directory containing the full filepath does not exist, create
        # all intermediary directories.
        if not os.path.exists(os.path.dirname(self.filepath)):
            os.makedirs(os.path.dirname(self.filepath))

        with open(self.filepath, 'w') as f:
            f.write('This string will be compressed')

    def test_zip(self):
        """It should compress a file and be able to decompress."""
        zip_path = util.zip_directory(self.compressdir, self.tmpdir)

        # Zip file should be smaller
        self.assertLess(os.path.getsize(self.filepath),
                        os.path.getsize(zip_path))

        # Zip file should be able to decompress and have same contents as
        # before.
        checkdir = os.path.join(self.tmpdir, 'check/')
        os.mkdir(checkdir)
        check_filename = os.path.join(checkdir, 'test/{}'.format(self.filename))
        with zipfile.ZipFile(zip_path) as f:
            f.extractall(checkdir)

        with open(check_filename) as f:
            s = f.read()
            self.assertEqual(s, 'This string will be compressed')

    def test_zip_multi_level(self):
        """It should support multiple directory levels."""
        self.create_file('test1/test.txt')
        self.create_file('test1/testsubdir/test.txt')
        self.create_file('test2/test.txt')
        zip_path = util.zip_directory(self.compressdir, self.tmpdir)
        with zipfile.ZipFile(zip_path) as f:
            names = f.namelist()
            self.assertIn('test/test1/test.txt', names)
            self.assertIn('test/test1/testsubdir/test.txt', names)
            self.assertIn('test/test2/test.txt', names)

    def test_zip_no_delete_original(self):
        """It should not delete the original files by default."""
        util.zip_directory(self.compressdir, self.tmpdir)
        self.assertTrue(os.path.exists(self.filepath))

    def test_zip_delete_original(self):
        """It should delete the original files if specified."""
        util.zip_directory(self.compressdir, self.tmpdir,
                           delete_original=True)
        self.assertFalse(os.path.exists(self.filepath))

    def test_zip_no_append(self):
        """It should not append files by default."""
        util.zip_directory(self.compressdir, self.tmpdir,
                           delete_original=True)
        self.create_file()
        zip_path = util.zip_directory(self.compressdir, self.tmpdir)
        with zipfile.ZipFile(zip_path) as f:
            self.assertEqual(len(f.namelist()), 1)

    def test_zip_append(self):
        """It should append files if specified."""
        zip_path = util.zip_directory(self.compressdir, self.tmpdir,
                                      delete_original=True, append=True)
        with zipfile.ZipFile(zip_path) as f:
            self.assertEqual(len(f.namelist()), 1)
        self.create_file()
        self.create_file()
        self.create_file()
        zip_path = util.zip_directory(self.compressdir, self.tmpdir,
                                      append=True)
        with zipfile.ZipFile(zip_path) as f:
            self.assertEqual(len(f.namelist()), 4)
