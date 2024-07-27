#!/usr/bin/env python3
#
# 2021 - 2023 Jan Provaznik (jan@provaznik.pro)
#
# Let's see how poorly this goes.

import setuptools
import sys
import os, os.path

VERSION = '0.9.0'

if not ('NOMAD_PATH' in os.environ):
    print('The $NOMAD_PATH environment variable is not set.')
    print('Please set it according to the README.')
    sys.exit(1)

NOMAD_PATH = os.environ['NOMAD_PATH']
if not os.path.isdir(NOMAD_PATH):
    print('The $NOMAD_PATH environment variable is set to "{}".'.format(NOMAD_PATH))
    print('However, it does not exist.'.format(NOMAD_PATH))
    sys.exit(1)

# We use static paths to NOMAD libraries.
#

NOMAD_PATH_BUILDS = os.path.join(NOMAD_PATH, 'build')
NOMAD_PATH_SOURCE = os.path.join(NOMAD_PATH, 'src')

NOMAD_PATH_LIB_NOMAD = os.path.join(NOMAD_PATH_BUILDS, 'src', 'libnomadStatic.a')
NOMAD_PATH_LIB_SGTEL = os.path.join(NOMAD_PATH_BUILDS, 'ext', 'sgtelib', 'libsgtelibStatic.a')

nomadlad_bridge = setuptools.Extension(
    name = 'nomadlad._nomadlad_bridge',
    sources = [ 'nomadlad/_bridge/nomadlad.cxx' ],
    libraries = [ 'boost_python3', 'boost_numpy3' ],
    include_dirs = [ NOMAD_PATH_SOURCE ],
    extra_objects = [ NOMAD_PATH_LIB_NOMAD, NOMAD_PATH_LIB_SGTEL
    ],
    define_macros = [ ('NOMADLAD_VERSION', '"{}"'.format(VERSION)) ],
    extra_compile_args = [ '-w', '-std=c++17', '-Wextra', '-pthread' ],
    language = 'c++'
)

# Yes, yes, yes!

setuptools.setup(
    name = 'nomadlad',
    version = VERSION,
    description = 'Basic interface for NOMAD 4.4.0 blackbox optimization software.',
    author = 'Jan Provaznik',
    author_email = 'jan@provaznik.pro',
    url = 'https://provaznik.pro/nomadlad',
    license = 'LGPL',
    ext_modules = [ nomadlad_bridge ],
    packages = [ 'nomadlad' ]
)

