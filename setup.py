#!/bin/python3
import fileinput
import os
import sys

import setuptools

from django_project_base import __version__


def write_ver_to_init(version="''"):
    replacement = "__version__ = '%s'\n" % (version)
    filename = 'django_project_base/__init__.py'
    for line in fileinput.input([filename], inplace=True):
        if line.strip().startswith('__version__'):
            line = replacement
        sys.stdout.write(line)


def get_version(version_arg):
    try:
        if version_arg == 'publish':
            print('Missing version argument.')
            sys.exit(1)
        all(map(int, version_arg.split('.', 2)))
    except Exception:
        print('Invalid version format. Should be x.y.z (all numbers)')
        sys.exit(1)
    return version_arg


with open('README.rst', 'r') as fh:
    long_description = fh.read()
with open('requirements.txt', 'r') as fh:
    requirements = fh.readlines()

version = __version__

if sys.argv[1] == 'publish':
    version = get_version(sys.argv[-1])

    if os.system('python -m wheel version'):
        print('wheel not installed.\nUse `pip install wheel`.\nExiting.')
        sys.exit()
    if os.system('python -m twine --version'):
        print('twine not installed.\nUse `pip install twine`.\nExiting.')
        sys.exit()
    if os.system('tox -e check'):
        sys.exit()

    write_ver_to_init(version)
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    os.system('rm -rf build && rm -rf dist && rm -rf django_project_base.egg-info')
    os.system('git checkout django_project_base/__init__.py')
    os.system('git tag -a %s -m \'version %s\'' % (version, version))
    os.system('git push --tags')
    sys.exit()


setuptools.setup(
    name="django-project-base",
    version=version,
    author="Jure Erznožnik",
    author_email="jure@velis.si",
    description="Everything revolves around it: users, roles, permissions, tags, etc.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/velis74/django-project-base",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.4',
    license='BSD-3-Clause',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
    ],
)
