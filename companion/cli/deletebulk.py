"""This command deletes documents from an index.

For Example:

    >>> companion delete myindex mydoctype -q \
    >>> '{"query":{"bool":{"filter":{"range":{"timestamp":{"gt":"2015"}}}}}'

For more complicated queries, you can store the query in a JSON file:

    >>> companion delete myindex mydoctype -q myquery.json

The command will automatically detect when a file is used.

"""
import os
import json
from ..api import deletebulk, util


def parse_query(query):
    """Parse the query argument for this command.

    :param query: A JSON compatible string or a filename.
    :type query: str
    :returns: A Python dict corresponding to the query.

    """
    if query is None:
        return query

    # If the query is actually a file, load it.
    # Otherwise assume it is a JSON string.
    if os.path.isfile(query):
        with open(query) as f:
            query = json.loads(f.read())
    else:
        query = json.loads(query)

    return query


def run(args):
    query = parse_query(args.query)

    client = util.get_client(args.url)
    cnt = client.count(index=args.index_name, doc_type=args.doc_type,
                       body=query)
    if query:
        cnt_without = client.count(index=args.index_name,
                                   doc_type=args.doc_type)
        print('You specified a query. Please double check the data...')
        print('Number of documents if query was empty: {}'
              .format(cnt_without['count']))
        print('Number of documents with your query: {}'.format(cnt['count']))

    print('Will delete {} documents'.format(cnt['count']))
    res = input('Does this look correct? Type "yes" if you are sure: ')
    if res != 'yes':
        return

    deletebulk.delete_by_query(args.url, args.index_name, args.doc_type, query)
