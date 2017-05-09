"""This module supplies various reindex functions.

"""
import logging

import dateutil.parser
from elasticsearch import helpers

from . import util


__all__ = ['date_reindex']
logger = logging.getLogger(__name__)


def date_reindex(url, source_index_name, target_index_name, date_field=None,
                 delete_docs=False, query=None, use_same_id=True,
                 scan_kwargs={}):
    """Re-index all documents in a source index to the target index.

    The re-index takes an optional query to limit the source documents.

    If a date field identifier is used, the target index name is assumed to be a
    template that will be called with the date field as a format parameter. This
    allows temporal re-indexing from e.g. "sourceindex" to
    "targetindex-2015-01-02". If not date field is given, the target index name
    is used as-is

    :param url: Cluster url
    :type url: str
    :param source_index_name: The name of the source index to re-index from.
    :type source_index_name: str
    :param target_index_name: The name of the target index to re-index to.
    :type target_index_name: str
    :param date_field: The name of a date field in the source documents to use
        for temporal re-indexing into the target index.
    :type date_field: str
    :param delete_docs: Whether or not to delete the source documents. Default
        is False.
    :type delete_docs: bool
    :param query: A query to use for the source documents
    :type query: dict
    :param use_same_id: Whether or not to use the same ID as the source. If
        True, will use the exact same ID as the source. If False, will re-create
        a new ID automatically. Default is True.
    :param scan_kwargs: Extra arguments for the index scanner. Similar to
        scan_kwargs in helpers.reindex
    :type scan_kwargs: dict
    :returns: The result of an iterating bulk operation.

    """
    # Inspired by the reindex helper in the elasticsearch lib
    logger.info('Starting reindex from {} to {}'
                .format(source_index_name, target_index_name))
    client = util.get_client(url)
    docs = helpers.scan(client,
                        index=source_index_name,
                        query=query,
                        scroll='5m',
                        **scan_kwargs)

    def _docs_to_operations(hits):
        for h in hits:
            if date_field and date_field not in h['_source']:
                logger.error('Date field not found in {}'.format(h['_id']))
                continue

            delete_op = None
            if delete_docs:
                delete_op = {
                    '_op_type': 'delete',
                    '_index': h['_index'],
                    '_type': h['_type'],
                    '_id': h['_id']
                }

            new_index_name = target_index_name
            if date_field:
                date_value = dateutil.parser.parse(h['_source'][date_field])
                new_index_name = new_index_name.format(date_value)
            h['_index'] = new_index_name

            if not use_same_id:
                del h['_id']

            if 'fields' in h:
                h.update(h.pop('fields'))

            yield h
            if delete_op is not None:
                yield delete_op

    kwargs = {
        'stats_only': True,
    }

    return helpers.bulk(client, _docs_to_operations(docs), chunk_size=1000,
                        **kwargs)
