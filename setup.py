# -*- coding: utf-8 -*-

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

__version__ = None
with open(path.join(here, 'cpc_api', '__version.py')) as __version:
    exec(__version.read())
assert __version__ is not None

with open(path.join(here, 'README.md')) as readme:
    LONG_DESC = readme.read()
    # are we using Python2 ? If yes, then decode.
    # If not, it raises AttributeError, that we should ignore
    try:  
        LONG_DESC = LONG_DESC.decode('utf-8')
    except AttributeError:
        # nothing to do here :
        # we are running Python3, the LONG_DESC str is already perfect
        pass
setup(
    name='cpc_api',
    version=__version__,

    description='Python api for nosdeputes.fr and nossenateurs.fr',
    long_description=LONG_DESC,
    license="MIT",

    url='https://github.com/regardscitoyens/cpc-api',
    author='Regards Citoyens',
    author_email='contact@regardscitoyens.org',

    include_package_data=True,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],

    keywords='api nosdeputes.fr nossenateurs.fr',

    packages=['cpc_api'],

    install_requires=['requests', 'fuzzywuzzy', 'matplotlib', 'imageio', 'numpy'],
)