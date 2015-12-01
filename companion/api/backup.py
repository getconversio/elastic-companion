"""Backup Elasticsearch documents to a datastore. Currently, only S3 is
supported.

"""
import os
import json
import shutil
import logging
import datetime
import tempfile

import boto3
from elasticsearch import helpers

from . import util
from .. import error

__all__ = ['s3']
logger = logging.getLogger(__name__)
now = datetime.datetime.utcnow()


def _cleanup(tmpdir):
    shutil.rmtree(tmpdir)


def _save_hit(root_path, hit):
    """Save a single Elasticsearch hit in JSON format.

    :param rootdir: The root path for storing the hit.
    :type rootdir: str
    :param hit: JSON compatible Elasticsearch hit.
    :type hit: dict
    :returns: The filepath for the created JSON file.

    """
    # Save the document in a subdir for the index_doctype pair.
    # E.g. tmpdir/event_click/event_click_abcd.json
    index_path = '{}/{}_{}'.format(root_path, hit['_index'], hit['_type'])
    doc_path = '{}/{}_{}_{}.json'.format(index_path,
                                         hit['_index'],
                                         hit['_type'],
                                         hit['_id'])
    if not os.path.exists(index_path):
        os.makedirs(index_path)
    with open(doc_path, 'w') as f:
        json.dump(hit, f)
    return doc_path


def _fetch_and_tar(url, index_name):
    client = util.get_client(url)
    if not client.indices.exists(index_name):
        logger.warn('Index "{}" does not exist, ignoring it'.format(index_name))
        return None, None

    tmpdir = tempfile.mkdtemp()
    logger.info('Fetching index documents {}'.format(index_name))
    logger.info('Storing documents in {}'.format(tmpdir))
    body = {'size': 1000}
    hits_iter = helpers.scan(client,
                             index=index_name,
                             query=body,
                             scroll='5m')
    index_dirs = set()
    for hit in hits_iter:
        doc_path = _save_hit(tmpdir, hit)
        index_dirs.add(os.path.dirname(doc_path))
    tar_files = []
    logger.info('Done fetching documents. Creating {} tar archives'
                .format(len(index_dirs)))
    for index_dir in index_dirs:
        tar_files.append(util.tar_gz_directory(index_dir, tmpdir))
    logger.info('Done creating tar files')
    return tmpdir, tar_files


def _flush_zips(index_dirs, target_dir):
    zip_files = []
    for index_dir in index_dirs:
        zip_files.append(util.zip_directory(index_dir, target_dir,
                                            delete_original=True,
                                            append=True))
    return zip_files


def _fetch_and_zip(url, index_name, batch_size=10000):
    client = util.get_client(url)
    if not client.indices.exists(index_name):
        logger.warn('Index "{}" does not exist, ignoring it'.format(index_name))
        return None, None

    tmpdir = tempfile.mkdtemp()

    logger.info('Fetching index documents {}'.format(index_name))
    logger.info('Storing documents in {}'.format(tmpdir))

    body = {'size': 1000}
    hits_iter = helpers.scan(client,
                             index=index_name,
                             query=body,
                             scroll='5m')
    index_dirs = set()
    zip_files = set()
    processed_in_batch = 0
    for hit in hits_iter:
        doc_path = _save_hit(tmpdir, hit)
        index_dirs.add(os.path.dirname(doc_path))
        processed_in_batch += 1
        if processed_in_batch == batch_size:
            zip_files.update(_flush_zips(index_dirs, tmpdir))
            processed_in_batch = 0
            index_dirs.clear()
    zip_files.update(_flush_zips(index_dirs, tmpdir))
    logger.info('Done fetching documents and creating zip files')
    return tmpdir, list(zip_files)


def s3(url, index_name, region, bucket_name, user_key, secret_key,
       filetype='zip'):
    """Make a backup of an Elasticsearch index and send the data to
    to Amazon S3. The data format can be either tar.gz-files or zip-files.

    :param url: The full Elasticsearch url
    :type url: str
    :param index_name: The name of the index to backup.
    :type index_name: str
    :param region: The S3 region that the bucket is located in.
    :type region: str
    :param bucket_name: The S3 bucket name.
    :type bucket_name: str
    :param user_key: S3 username/access key
    :type user_key: str
    :param secret_key: S3 password/secret key
    :type secret_key: str
    :param filetype: Type of file to send to S3.
    :type filetype: str

    """
    logger.info('Starting S3 backup for index {}'.format(index_name))

    if filetype == 'zip':
        tmpdir, files = _fetch_and_zip(url, index_name)
    elif filetype == 'tar':
        tmpdir, files = _fetch_and_tar(url, index_name)
    else:
        raise error.CompanionException('Unknown filetype {}'.format(filetype))

    if not files:
        return logger.warn('No files to upload, exiting')

    backup_dir = 'clibackup/{:%Y/%m/%d_%H%M%S}'.format(now)
    logger.info('Starting s3 upload to {}'.format(backup_dir))
    s3 = boto3.resource('s3',
                        region_name=region,
                        aws_access_key_id=user_key,
                        aws_secret_access_key=secret_key)
    bucket = s3.Bucket(bucket_name)
    for f in files:
        filename = os.path.basename(f)
        logger.info('Uploading object to s3: {}'.format(filename))
        object_key = '{}_{}'.format(backup_dir, filename)
        with open(f, 'rb') as data:
            bucket.put_object(Key=object_key, Body=data)
    logger.info('Done uploading objects to s3. Starting cleanup')
    _cleanup(tmpdir)
