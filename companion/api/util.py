"""Common utility functions used across commands."""
import os
import json
import shutil
import tarfile
import zipfile

import certifi
import elasticsearch


def pretty(output):
    return json.dumps(output, indent=2)


def get_client(url):
    is_ssl = url.startswith('https')
    return elasticsearch.Elasticsearch(url,
                                       use_ssl=is_ssl,
                                       verify_certs=is_ssl,
                                       ca_certs=certifi.where(),
                                       retry_on_timeout=True)


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


def zip_directory(directory, target_path, append=False, delete_original=False):
    """Zip the contents of a single directory.

    The zip-file will have the same name as the basename of the directory.

    :param directory: The directory to tar the contents of.
    :type directory: str
    :param target_path: The target of the compressed tar file.
    :type target_path: str
    :param append: Determine whether or not to append to an existing archive. If
        False, a new archive will always be created. Default is False.
    :type append: bool
    :param delete_original: Determine whether or not to delete the directory
        that was zipped. Default is False.
    :type append: bool
    :returns: The full path to the created zip file.

    """
    full_directory = os.path.abspath(os.path.normpath(directory))
    directory_name = os.path.basename(full_directory)
    zip_path = '{}/{}.zip'.format(target_path, directory_name)
    if os.path.exists(zip_path) and not append:
        os.remove(zip_path)

    mode = 'a' if append else 'w'
    with zipfile.ZipFile(zip_path, mode=mode,
                         compression=zipfile.ZIP_DEFLATED) as zf:
        for dirpath, _, filenames in os.walk(full_directory):
            for filename in filenames:
                # Find the full filepath for the filename
                # For storing the file in the zip, remove the part of the
                # full path that contains directory structures above the
                # directory being zipped
                # For example, /home/user/mydirectory/myfile.txt becomes
                # mydirectory/myfile.txt in the zipfile.
                full_filepath = os.path.join(dirpath, filename)
                short_filepath = os.path.relpath(full_filepath,
                                                 start=full_directory)
                short_filepath = os.path.join(directory_name, short_filepath)
                zf.write(full_filepath, short_filepath)

    if delete_original:
        shutil.rmtree(directory)

    return zip_path
