import os
import io
import sys
from setuptools import setup, find_packages

from uwsgiconf import VERSION


PATH_BASE = os.path.dirname(__file__)
PYTEST_RUNNER = ['pytest-runner'] if 'test' in sys.argv else []


def get_readme():
    # This will return README (including those with Unicode symbols).
    with io.open(os.path.join(PATH_BASE, 'README.rst')) as f:
        return f.read()


setup(
    name='uwsgiconf',
    version='.'.join(map(str, VERSION)),
    url='https://github.com/idlesign/uwsgiconf',

    description='Configure uWSGI from your Python code',
    long_description=get_readme(),
    license='BSD 3-Clause License',

    author='Igor `idle sign` Starikov',
    author_email='idlesign@yandex.ru',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=[],
    setup_requires=[] + PYTEST_RUNNER,
    extras_require={
        'cli':  ['click>=2.0'],
    },

    entry_points={
        'console_scripts': ['uwsgiconf = uwsgiconf.cli:main'],
    },

    test_suite='tests',
    tests_require=[
        'pytest',
        'pytest-stub',
    ],

    classifiers=[
        # As in https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: BSD License'
    ],
)
