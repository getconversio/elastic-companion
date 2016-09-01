"""Testing."""
import os
import datetime

from elasticsearch import Elasticsearch


es_url = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')


def create_test_data():
    # Add some test data to Elasticsearch.
    es = Elasticsearch(es_url)
    es.indices.delete(index='companiontest', ignore=[404])
    es.indices.create(index='companiontest',
                      body={
                          'index': {
                              'number_of_shards': 1,
                              'number_of_replicas': 0
                          }
                      })

    # Create 3 "simple" doc types and 1 "advanced"
    es.create(index='companiontest',
              doc_type='simple',
              id='foo',
              body={
                  'timestamp': datetime.datetime(2015, 1, 1),
                  'id': 'foo'
              })
    es.create(index='companiontest',
              doc_type='simple',
              id='bar',
              body={
                  'timestamp': datetime.datetime(2015, 1, 2),
                  'id': 'bar'
              })
    es.create(index='companiontest',
              doc_type='simple',
              id='baz',
              body={
                  'timestamp': datetime.datetime(2015, 1, 3),
                  'id': 'baz'
              })

    es.create(index='companiontest',
              doc_type='advanced',
              id='foo',
              body={
                  'timestamp': datetime.datetime(2015, 1, 1),
                  'id': 'foo'
              })

    es.indices.refresh(index='companiontest')
