"""Health command."""
from ..api import health


def run(args):
    health.health(args.url, args.level)
