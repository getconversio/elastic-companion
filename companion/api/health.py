"""Health API. Thin wrapper around the Elasticsearch health command."""
import logging
from . import util

__all__ = ['health']
logger = logging.getLogger(__name__)


def health(url, level):
    es = util.get_client(url)
    logger.info(util.pretty(es.cluster.health(level=level)))
