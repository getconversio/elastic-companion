"""This module supplies various reindex functions.

"""
import logging

import dateutil.parser
from elasticsearch import helpers

from . import util


__all__ = ['date_reindex']
logger = logging.getLogger(__name__)


def date_reindex(url, source_index_name, target_index_name, date_field=None,
                 delete_docs=False, query=None):
    # Inspired by the reindex helper in the elasticsearch lib
    logger.info('Starting reindex from {} to {}'
                .format(source_index_name, target_index_name))
    client = util.get_client(url)
    docs = helpers.scan(client,
                        index=source_index_name,
                        query=query,
                        scroll='5m',
                        fields=('_source', '_parent', '_routing', '_timestamp'))

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
