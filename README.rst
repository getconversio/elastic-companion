elastic-companion
=================

A command-line tool and API for various Elasticsearch operations.

.. image:: https://travis-ci.org/getconversio/elastic-companion.svg?branch=master
    :target: https://travis-ci.org/getconversio/elastic-companion

Install
-------

    pip install elastic-companion

**Note**: The 1.X versions of elastic-companion support Elasticsearch 1.X and
the 5.X versions support Elasticsearch 5.X. This is similar to the versioning
of the official library

Commands
--------

To see the list of commands, use the ``-h`` or ``--help`` flag.

Each command has a corresponding Python module that can be imported and used as
an API rather than from the command-line.

### `setup`

The `setup` command will load all indexes, mappings, templates and scripts from the data directory, and send them to ES.

#### `/scripts`

The scripts folder should have `.json` files which act as script descriptors. Each file should have the content:

```json
{
    "id": "SCRIPT_ID",
    "lang": "SCRIPT_LANG",
    "body": "SCRIPT_BODY",
    "path": "SCRIPT_BODY_FILE_PATH"
}
```

While `id` and `lang` are required and should match the requirements of ES. These will determine how each script is stored. The values `body` and `path`, however, are mutually exclusive and only one is required. You can specify the script's body directly inline under `body`, or point to a file using `path`.

Developing
----------

If you are using Docker and Docker Compose, then you don't need to fiddle with
python and pip manually. Otherwise, see below.

Download Python 3, then::

    $ pyvenv-3.X venv
    $ source venv/bin/activate
    $ pip3 install -r requirements.txt
    $ ./cli.py -h

On Ubuntu, there's a bit of an issue with ``pip3`` and the above might not work.
Then::

    $ pyvenv-3.X venv --without-pip
    $ source venv/bin/activate
    $ cd venv
    $ wget https://bootstrap.pypa.io/get-pip.py
    $ python3 get-pip.py
    $ cd ..
    $ pip3 install -r requirements.txt
    $ ./cli.py -h

Testing
-------

Use ``nose``::

    $ nosetests

or::

    $ docker-compose run --rm companion nosetests

Deploying
---------

You need access to the pypi repository first, then it's just a matter of::

    $ python setup.py sdist bdist_wheel
    $ twine upload dist/*
