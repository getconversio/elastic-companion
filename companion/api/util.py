"""Common utility functions used across commands."""
import os
import json
import tarfile

import certifi
import elasticsearch


def pretty(output):
    return json.dumps(output, indent=2)


def get_client(url):
    is_ssl = url.startswith('https')
    return elasticsearch.Elasticsearch(url,
                                       use_ssl=is_ssl,
                                       verify_certs=is_ssl,
                                       ca_certs=certifi.where())


def tar_gz_directory(directory, target_path):
    """Gzip and tar the contents of a single directory.

    The tar file will have the same name as the basename of the directory.

    :param directory: The directory to tar the contents of.
    :type directory: str
    :param target_path: The target of the compressed tar file.
    :type target_path: str
    :returns: The full path to the created tar.gz file.

    """
    directory_name = os.path.basename(os.path.normpath(directory))
    tar_path = '{}/{}.tar.gz'.format(target_path, directory_name)
    if os.path.exists(tar_path):
        os.remove(tar_path)
    with tarfile.open(tar_path, 'w:gz') as tar:
        tar.add(directory, directory_name)
    return tar_path
