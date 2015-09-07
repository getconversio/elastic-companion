"""Backup Elasticsearch documents to a datastore. Currently, only S3 is
supported.

For Example:

    >>> $ ./cli.py backup s3 myindex mybucket -u myuser -s mysecret

"""
from ..api import backup


def s3_run(args):
    backup.s3(args.url, args.index_name, args.region, args.bucket_name,
              args.user, args.secret)
