elastic-companion
=================

A command-line tool and API for various Elasticsearch operations.

Install
-------

    pip install elastic-companion

Commands
--------

To see the list of commands, use the ``-h`` or ``--help`` flag.

Each command has a corresponding Python module that can be imported and used as
an API rather than from the command-line.

Developing
----------

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
    $ wget https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py
    $ python3 get-pip.py
    $ cd ..
    $ pip3 install -r requirements.txt
    $ ./cli.py -h

Testing
-------

Use ``nose``::

    $ python setup.py nosetests
