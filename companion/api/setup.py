"""Setup API."""
import os
import glob
import json
import logging

from . import util
from .. import error

__all__ = ['IndexMapper']
logger = logging.getLogger(__name__)


class IndexMapper:
    """A simple index mapper that reads mapping definitions from JSON files and
    updates the target elasticsearch host with the mapping definitions.

    """
    def __init__(self, url, data_path='./data', delete_indexes=False):
        if not os.path.exists(data_path):
            raise error.CompanionException(
                'Data directory {} does not exist'.format(data_path))
        self.data_path = data_path
        self.delete_indexes = delete_indexes

        logger.info('Connecting to {}'.format(url))
        self.es = util.get_client(url)

    def run(self):
        indexes = self.get_settings()
        mappings = self.get_mappings()
        templates = self.get_templates()

        for index_name in indexes:
            if self.delete_indexes:
                self.delete_index(index_name)

            self.create_index(index_name, indexes[index_name])

        for index_name in mappings:
            for type_name in mappings[index_name]:
                self.update_mapping(index_name,
                                    type_name,
                                    mappings[index_name][type_name])

        for template_name in templates:
            self.update_template(template_name, templates[template_name])

    def get_settings(self):
        """Builds a settings dict from indexes in the index folder.

        The dict has the format:
        {
            index_name: {
                setup_dict
            }
        }

        """
        index_settings = {}
        for path in glob.iglob(self.data_path + '/index/*.json'):
            logger.debug('Reading index setup from {}'.format(path))
            setup = None
            with open(path) as f:
                setup = json.load(f)
            index_name = setup['index']
            index_setup = setup['setup']
            index_settings[index_name] = index_setup
        return index_settings

    def get_templates(self):
        """Builds a templates dict from index templates in the templates folder.

        The dict has the format:
        {
            template_name: {
                template_body
            }
        }

        """
        index_templates = {}
        for path in glob.iglob(self.data_path + '/template/*.json'):
            logger.debug('Reading index template setup from {}'.format(path))
            index_template = None
            with open(path) as f:
                index_template = json.load(f)
            template_name = index_template['name']
            setup_body = index_template['body']
            index_templates[template_name] = setup_body
        return index_templates

    def get_mappings(self):
        """Builds a mapping dict from all index mappings in the mappings folder.

        The dict has the format:
        {
            index_name: {
                type_name1: {
                    type_name1_mapping
                },
                type_name2: {
                    type_name2_mapping
                }
            }
        }

        """
        mappings = {}
        for path in glob.iglob(self.data_path + '/mapping/*.json'):
            logger.debug('Reading mapping from {}'.format(path))
            mapping = None
            with open(path) as f:
                mapping = json.load(f)
            index_name = mapping['index']
            type_name = mapping['type']
            type_mapping = mapping['mapping']
            if index_name not in mappings:
                mappings[index_name] = {}
            mappings[index_name][type_name] = type_mapping
        return mappings

    def create_index(self, index_name, settings):
        logger.info('Creating index {}'.format(index_name))
        self.es.indices.create(index=index_name, body=settings, ignore=400)

    def delete_index(self, index_name):
        logger.info('Deleting index {}'.format(index_name))
        self.es.indices.delete(index=index_name, ignore=[400, 404])

    def update_mapping(self, index_name, type_name, mapping):
        logger.info('Updating type {} on index {}'
                    .format(type_name, index_name))
        self.es.indices.put_mapping(index=index_name,
                                    doc_type=type_name,
                                    body=mapping)

    def update_template(self, template_name, template_definition):
        logger.info('Updating template definition {}'.format(template_name))
        self.es.indices.put_template(name=template_name,
                                     body=template_definition)
