"""This command re-indexes an index to a different index name. Useful for
temporal re-indexing.

For Example:

    >>> companion reindex event event-{:%Y} -d timestamp --deletedoc

"""
import datetime

from ..api import reindex


def run(args):
    if args.datefield:
        example = args.target_index_name.format(datetime.datetime.now())
        print('Target index name would be for example: {}'.format(example))
        res = input('Is this what you want? Type "yes" if you are sure: ')
        if res != 'yes':
            return

    reindex.date_reindex(args.url, args.source_index_name,
                         args.target_index_name, date_field=args.datefield,
                         delete_docs=args.deletedoc)
