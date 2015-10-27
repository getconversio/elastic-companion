from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='elastic-companion',
    version='0.9.6',
    description='Useful commands for Elasticsearch',
    long_description=long_description,
    url='https://github.com/receiptful/elastic-companion',
    author='Receiptful',
    author_email='dev@receiptful.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    keywords='elasticsearch cli',
    packages=['companion', 'companion.api', 'companion.cli'],
    install_requires=[
        'elasticsearch>=1.0.0,<2.0.0',
        'certifi==2015.4.28',
        'boto3==1.1.3',
        'python-dateutil==2.4.2'
    ],
    extras_require={
        'dev': ['twine', 'wheel', 'nose', 'coverage']
    },
    entry_points={
        'console_scripts': [
            'companion=companion:main',
        ],
    },
    test_suite='test.run'
)
