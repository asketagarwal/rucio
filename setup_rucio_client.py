'''
 Copyright European Organization for Nuclear Research (CERN)

  Licensed under the Apache License, Version 2.0 (the "License");
  You may not use this file except in compliance with the License.
  You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

  Authors:
  - Vincent Garonne, <vincent.garonne@cern.ch>, 2011-2017
  - Mario Lassnig, <mario.lassnig@cern.ch>, 2012-2013
  - Martin Barisits, <martin.barisits@cern.ch>, 2016-2017
'''

import os
import re
import shutil
import subprocess
import sys

from distutils.command.sdist import sdist as _sdist  # pylint:disable=no-name-in-module,import-error
from setuptools import setup

sys.path.insert(0, os.path.abspath('lib/'))

from rucio import version  # noqa

if sys.version_info < (2, 5):
    print 'ERROR: Rucio requires at least Python 2.6 to run.'
    sys.exit(1)
sys.path.insert(0, os.path.abspath('lib/'))


# Arguments to the setup script to build Basic/Lite distributions
COPY_ARGS = sys.argv[1:]
NAME = 'rucio-clients'
IS_RELEASE = False
PACKAGES = ['rucio', 'rucio.client', 'rucio.common',
            'rucio.rse.protocols', 'rucio.rse', 'rucio.tests']
REQUIREMENTS_FILES = ['tools/pip-requires-client']
DESCRIPTION = "Rucio Client Lite Package"
DATA_FILES = [('etc/', ['etc/rse-accounts.cfg.template', 'etc/rucio.cfg.template', 'etc/rucio.cfg.atlas.client.template']),
              ('tools/', ['tools/pip-requires-client', ]), ]

SCRIPTS = ['bin/rucio', 'bin/rucio-admin']
if os.path.exists('build/'):
    shutil.rmtree('build/')
if os.path.exists('lib/rucio_clients.egg-info/'):
    shutil.rmtree('lib/rucio_clients.egg-info/')
if os.path.exists('lib/rucio.egg-info/'):
    shutil.rmtree('lib/rucio.egg-info/')

if '--release' in COPY_ARGS:
    IS_RELEASE = True
    COPY_ARGS.remove('--release')


# If Sphinx is installed on the box running setup.py,
# enable setup.py to build the documentation, otherwise,
# just ignore it
cmdclass = {}

try:
    from sphinx.setup_command import BuildDoc

    class local_BuildDoc(BuildDoc):
        '''
        local_BuildDoc
        '''
        def run(self):
            '''
            run
            '''
            for builder in ['html']:   # 'man','latex'
                self.builder = builder
                self.finalize_options()
                BuildDoc.run(self)
    cmdclass['build_sphinx'] = local_BuildDoc
except:
    pass


def get_reqs_from_file(requirements_file):
    '''
    get_reqs_from_file
    '''
    if os.path.exists(requirements_file):
        return open(requirements_file, 'r').read().split('\n')
    return []


def parse_requirements(requirements_files):
    '''
    parse_requirements
    '''
    requirements = []
    for requirements_file in requirements_files:
        for line in get_reqs_from_file(requirements_file):
            if re.match(r'\s*-e\s+', line):
                requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
            elif re.match(r'\s*-f\s+', line):
                pass
            else:
                requirements.append(line)
    return requirements


def parse_dependency_links(requirements_files):
    '''
    parse_dependency_links
    '''
    dependency_links = []
    for requirements_file in requirements_files:
        for line in get_reqs_from_file(requirements_file):
            if re.match(r'(\s*#)|(\s*$)', line):
                continue
            if re.match(r'\s*-[ef]\s+', line):
                dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))
    return dependency_links


def write_requirements():
    '''
    write_requirements
    '''
    venv = os.environ.get('VIRTUAL_ENV', None)
    if venv is not None:
        req_file = open("requirements.txt", "w")
        output = subprocess.Popen(["pip", "freeze", "-l"], stdout=subprocess.PIPE)
        requirements = output.communicate()[0].strip()
        req_file.write(requirements)
        req_file.close()


REQUIRES = parse_requirements(requirements_files=REQUIREMENTS_FILES)
DEPEND_LINKS = parse_dependency_links(requirements_files=REQUIREMENTS_FILES)


class CustomSdist(_sdist):
    '''
    CustomSdist
    '''
    user_options = [
        ('packaging=', None, "Some option to indicate what should be packaged")
    ] + _sdist.user_options

    def __init__(self, *args, **kwargs):
        '''
        __init__
        '''
        _sdist.__init__(self, *args, **kwargs)
        self.packaging = "default value for this option"

    def get_file_list(self):
        '''
        get_file_list
        '''
        print "Chosen packaging option: " + NAME
        self.distribution.data_files = DATA_FILES
        _sdist.get_file_list(self)


cmdclass['sdist'] = CustomSdist

setup(
    name=NAME,
    version=version.version_string(),
    packages=PACKAGES,
    package_dir={'': 'lib'},
    data_files=DATA_FILES,
    script_args=COPY_ARGS,
    cmdclass=cmdclass,
    include_package_data=True,
    scripts=SCRIPTS,
    # doc=cmdclass,
    author="Rucio",
    author_email="rucio-dev@cern.ch",
    description=DESCRIPTION,
    license="Apache License, Version 2.0",
    url="http://rucio.cern.ch/",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Environment :: No Input/Output (Daemon)', ],
    install_requires=REQUIRES,
    dependency_links=DEPEND_LINKS,
)
