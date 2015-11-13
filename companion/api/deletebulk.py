"""This module supplies a convenient delete function for doing bulk deletes.

"""
import logging

from elasticsearch import helpers

from . import util


__all__ = ['delete_by_query']
logger = logging.getLogger(__name__)


def delete_by_query(url, index_name, doc_type, query):
    """Deletes all documents for the given index and document type.

    :param url: A full connection url.
    :param index_name: The name of the index to delete from.
    :param doc_type: The name of the document type to delete.
    :param query: A query body. If provided as None, all documents will be
    deleted.

    """
    # Inspired by the reindex helper in the elasticsearch lib
    logger.info('Starting delete bulk on index {} and doc type {}'
                .format(index_name, doc_type))
    client = util.get_client(url)
    docs = helpers.scan(client,
                        index=index_name,
                        doc_type=doc_type,
                        query=query,
                        scroll='5m')

    def _docs_to_operations(hits):
        for h in hits:
            delete_op = {
                '_op_type': 'delete',
                '_index': h['_index'],
                '_type': h['_type'],
                '_id': h['_id']
            }
            yield delete_op

    kwargs = {
        'stats_only': True,
    }

    stats = helpers.bulk(client, _docs_to_operations(docs), chunk_size=1000,
                         **kwargs)
    logger.info('Finished bulk delete, statistics:')
    logger.info(stats)
