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
    logger.info('Fetching index documents {}'.format(index_name))
    tmpdir = tempfile.mkdtemp()
    logger.info('Storing documents in {}'.format(tmpdir))
    client = util.get_client(url)
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


def s3(url, index_name, region, bucket_name, user_key, secret_key):
    logger.info('Starting S3 backup for index {}'.format(index_name))
    tmpdir, tar_files = _fetch_and_tar(url, index_name)
    backup_dir = 'clibackup/{:%Y/%m/%d_%H%M%S}'.format(now)
    logger.info('Starting s3 upload to {}'.format(backup_dir))
    s3 = boto3.resource('s3',
                        region_name=region,
                        aws_access_key_id=user_key,
                        aws_secret_access_key=secret_key)
    bucket = s3.Bucket(bucket_name)
    for tar_file in tar_files:
        tar_filename = os.path.basename(tar_file)
        logger.info('Uploading object to s3: {}'.format(tar_filename))
        object_key = '{}_{}'.format(backup_dir, tar_filename)
        with open(tar_file, 'rb') as data:
            bucket.put_object(Key=object_key, Body=data)
    logger.info('Done uploading objects to s3. Starting cleanup')
    _cleanup(tmpdir)
