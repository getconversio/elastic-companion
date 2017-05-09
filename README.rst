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
