from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='elastic-companion',
    version='5.1.0',
    description='Useful commands for Elasticsearch',
    long_description=long_description,
    url='https://github.com/getconversio/elastic-companion',
    author='Conversio',
    author_email='dev@conversio.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    keywords='elasticsearch cli',
    packages=['companion', 'companion.api', 'companion.cli'],
    install_requires=[
        'elasticsearch>=5.0.0,<6.0.0',
        'certifi>=2016.8.31',
        'boto3==1.4.0',
        'python-dateutil==2.5.3'
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
