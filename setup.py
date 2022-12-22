#!/usr/bin/env python3
#
# 2021 - 2023 Jan Provaznik (jan@provaznik.pro)
#
# Let's see how poorly this goes.

import setuptools
import sys
import os, os.path

VERSION = '0.5.0'

if not ('NOMAD_HOME' in os.environ):
    print('The $NOMAD_HOME environment variable is not set.')
    print('Please set it according to the official NOMAD installation guide.')
    print('https://nomad-4-user-guide.readthedocs.io/en/latest/Installation.html')
    sys.exit(1)

NOMAD_HOME = os.environ['NOMAD_HOME']

if not os.path.isdir(NOMAD_HOME):
    print('The $NOMAD_HOME environment variable is set to "{}".'.format(NOMAD_HOME))
    print('However, it does not exist.'.format(NOMAD_HOME))
    sys.exit(1)

BUILD_PATH = 'build/release'
NOMAD_PATH = os.path.join(NOMAD_HOME, BUILD_PATH)

if not os.path.isdir(NOMAD_PATH):
    print('The $NOMAD_HOME environment variable is set to "{}" and it exists.'.format(NOMAD_HOME))
    print('However, it looks like the library is not compiled properly.')
    print('We expect "{}" to exist.'.format(NOMAD_PATH))
    sys.exit(1)

NOMAD_PATH_LIB = os.path.join(NOMAD_PATH, 'lib')
NOMAD_PATH_INC = os.path.join(NOMAD_PATH, 'include')

# We use static paths to NOMAD libraries.
#
# Alternatively one could provide appropriate configuration to ld.so.conf and
# have the operating system handle it on its own.

nomadlad_bridge = setuptools.Extension(
    name = 'nomadlad._bridge',
    sources = [ 'nomadlad/_bridge/nomadlad.cxx' ],
    libraries = [ 'boost_python3', 'boost_numpy3', 'nomadAlgos', 'nomadUtils', 'nomadEval' ],
    library_dirs = [ NOMAD_PATH_LIB ],
    include_dirs = [ NOMAD_PATH_INC ],
    define_macros = [ ('NOMADLAD_VERSION', '"{}"'.format(VERSION)) ],
    extra_compile_args = [ '-std=c++17', '-Wextra', '-pthread' ],
    extra_link_args = [ '-Wl,-rpath,{}'.format(NOMAD_PATH_LIB) ],
    language = 'c++'
)

# Yes, yes, yes!

setuptools.setup(
    name = 'nomadlad',
    version = VERSION,
    description = 'Basic interface for NOMAD 4.3.0 blackbox optimization software.',
    author = 'Jan Provaznik',
    author_email = 'jan@provaznik.pro',
    url = 'https://provaznik.pro/nomadlad',
    license = 'LGPL',
    ext_modules = [ nomadlad_bridge ],
    packages = [ 'nomadlad' ]
)

