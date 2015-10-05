"""Setup command."""
from ..api import setup


def run(args):
    if args.reset:
        # Prompt the user to be extra sure.
        res = input('THIS WILL DELETE ALL DATA! Type "yes" if you are sure: ')
        if res != 'yes':
            return
    im = setup.IndexMapper(args.url,
                           data_path=args.data_path,
                           delete_indexes=args.reset)
    im.run()
