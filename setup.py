#!/usr/bin/env python3
#
# 2021 - 2023 Jan Provaznik (jan@provaznik.pro)
#
# Let's see how poorly this goes.

import pybind11.setup_helpers
import setuptools
import sys
import os, os.path

VERSION = '0.9.2'

# Environment processing
#

env_nomad_path = os.environ.get('NOMAD_PATH')
env_nomad_msvc = os.environ.get('NOMAD_MSVC')

if not(env_nomad_path):
    print('Missing $NOMAD_PATH environment variable.')
    sys.exit(1)

# Of course, Windows needs special treatment.
#

setup_compile_args = []
setup_include_paths = []
setup_library_names = []
setup_library_paths = []
setup_objects_paths = []

if env_nomad_msvc:
  setup_compile_args.append('/std:c++17')
else:
  setup_compile_args.append('-std=c++17')
  setup_compile_args.append('-Wall')

if env_nomad_msvc:
  setup_library_names.append('nomadStatic')
  setup_library_names.append('sgtelibStatic')
  setup_library_paths.append(
    os.path.join(env_nomad_path, 'build', 'src', 'Release'))
  setup_library_paths.append(
    os.path.join(env_nomad_path, 'build', 'ext', 'sgtelib', 'Release'))
else:
  setup_objects_paths.append(
    os.path.join(env_nomad_path, 'build', 'src', 'libnomadStatic.a'))
  setup_objects_paths.append(
    os.path.join(env_nomad_path, 'build', 'ext', 'sgtelib', 'libsgtelibStatic.a'))

setup_include_paths.append(
  os.path.join(env_nomad_path, 'src'))

# C++ module
#

nomadlad_bridge = pybind11.setup_helpers.Pybind11Extension(
    name = 'nomadlad._nomadlad_bridge',
    sources = [ 'nomadlad/_bridge/nomadlad.cxx' ],
    define_macros = [ ('NOMADLAD_VERSION', f'"{VERSION}"') ],
    libraries = setup_library_names,
    library_dirs = setup_library_paths,
    include_dirs = setup_include_paths,
    extra_objects = setup_objects_paths,
    extra_compile_args = setup_compile_args,
    language = 'c++'
)

# Yes, yes, yes!
#

setuptools.setup(
    name = 'nomadlad',
    version = VERSION,
    description = 'Interface for NOMAD 4.4.0 blackbox optimization software.',
    author = 'Jan Provaznik',
    author_email = 'jan@provaznik.pro',
    url = 'https://github.com/jan-provaznik/nomadlad',
    license = 'LGPL-3.0',
    ext_modules = [ nomadlad_bridge ],
    packages = [ 'nomadlad' ]
)

