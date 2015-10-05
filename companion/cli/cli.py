# This script should usually only be run once for a deployment, but can also be
# augmented later with new mappings. In general, using the dynamic mapping
# feature will work just fine.

# Tips for anyone reading this.
# - Email fields: By default, they are automatically analyzed and hence parsed
# into tokens before and after the @ which is probably not very good for
# queries.
import logging
import argparse

from . import setup, health, reindex, backup


# Create main parser
parser = argparse.ArgumentParser(description='CLI tool for Elastic search.')
parser.add_argument('-u', '--url', help='The host url to connect to',
                    default='http://localhost:9200')
parser.add_argument('--log-level', help='The log level', default='INFO')
command_parser = parser.add_subparsers(help='Command options', dest='command')

# http://stackoverflow.com/a/23354355/2021517
command_parser.required = True

# Create parser for status command
health_parser = command_parser.add_parser('health',
                                          help='Shows health of the cluster')
health_parser.add_argument('-l', '--level', help='The status level',
                           choices=['cluster', 'indices', 'shards'],
                           default='cluster')
health_parser.set_defaults(func=health.run)

# Create parser for setup command
setup_parser = command_parser.add_parser('setup', help='Perform index setup')
setup_parser.add_argument('-r', '--reset', action='store_true',
                          help="""Reset indexes before updating, BE CAREFUL,
                          THIS WILL DELETE ALL DATA""")
setup_parser.add_argument('-p', '--data-path',
                          help='Directory containing the setup data files',
                          default='./data')
setup_parser.set_defaults(func=setup.run)

# Create parser for status command
reindex_parser = command_parser.add_parser('reindex', help='Re-index an index')
reindex_parser.add_argument('source_index_name',
                            help='The name of the index to re-index')
reindex_parser.add_argument('target_index_name',
                            help='''The target index name. The name can be
                            specific such as "myindex" or use a date pattern
                            such as "myindex-{:%%Y-%%m-%%d}". The date for a
                            date pattern is read from the field specified by the
                            DATEFIELD parameter''')
reindex_parser.add_argument('-d', '--datefield',
                            help='The field to base the date on')
reindex_parser.add_argument('--deletedoc', help='Delete the source document',
                            action='store_true')
reindex_parser.set_defaults(func=reindex.run)

# Create parser for backup command
backup_parser = command_parser.add_parser('backup',
                                          help='Backup an index')
backup_type_parser = backup_parser.add_subparsers(help='Storage type',
                                                  dest='storagetype')
s3_parser = backup_type_parser.add_parser('s3', help='Backup to AWS S3')
s3_parser.add_argument('index_name', help='The name of bucket to backup to')
s3_parser.add_argument('bucket_name', help='The name of bucket to backup to')
s3_parser.add_argument('-r', '--region', help='The name of aws region',
                       default='eu-west-1')
s3_parser.add_argument('-u', '--user', help='User key for s3')
s3_parser.add_argument('-s', '--secret', help='Secret key for s3')
s3_parser.set_defaults(func=backup.s3_run)


def main():
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)
    args.func(args)


if __name__ == '__main__':
    """When run from the command-line, set a standard handler and formatter."""
    main()
