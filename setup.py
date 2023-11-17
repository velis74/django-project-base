#!/bin/python3
import fileinput
import os
import sys

import setuptools

from django_project_base import __version__

publish_local = True


def write_ver_to_init(file_name: str, version: str, search: str, replacement: str):
    replacement = replacement % version
    filename = file_name
    for line in fileinput.input([filename], inplace=True):
        if line.strip().startswith(search):
            line = replacement
        sys.stdout.write(line)


def get_version(version_arg):
    from versio.version import Version
    from versio.version_scheme import Simple3VersionScheme

    try:
        if version_arg == "publish":
            print("Missing version argument.")
            sys.exit(1)
        Version(version_arg, scheme=Simple3VersionScheme)
    except Exception:
        print("Invalid version format. Should be x.y.z (all numbers)")
        sys.exit(1)
    return version_arg


with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()

for lnum, line in enumerate(requirements):
    if line[:3] == "git":
        requirements.pop(lnum)

version = __version__

if sys.argv[1] == "publish":
    version_str = get_version(sys.argv[-1])

    if os.system("python -m wheel version"):
        print("wheel not installed.\nUse `pip install wheel`.\nExiting.")
        sys.exit()
    if os.system("python -m twine --version"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    if os.system("tox -e check") or os.system("npm run test"):
        sys.exit()

    write_ver_to_init("django_project_base/__init__.py", version_str, "__version__", "__version__ = '%s'\n")
    write_ver_to_init("package.json", version_str, '"version": ', '  "version": "%s",\n')

    os.system("npm run build")
    os.system("npm publish --access=public")
    os.system("rm -rf build && rm -rf dist && rm -rf django_project_base.egg-info")

    os.system("python setup.py sdist bdist_wheel")
    # if you don't like to enter username / pass for pypi every time, run this command:
    #  keyring set https://upload.pypi.org/legacy/ username  (it will ask for password)
    os.system("twine upload dist/*")

    os.system("rm -rf build && rm -rf dist && rm -rf django_project_base.egg-info")
    os.system("git checkout django_project_base/__init__.py")
    os.system("git checkout package.json")
    os.system("git tag -a %s -m 'version %s'" % (version_str, version_str))
    os.system("git push --tags")
    sys.exit()

setuptools.setup(
    name="django-project-base",
    version=version,
    author="Jure Erznožnik",
    author_email="jure@velis.si",
    description="Everything revolves around it: users, roles, permissions, tags, etc.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/velis74/django-project-base",
    packages=setuptools.find_packages(include=("django_project_base",)),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    license="BSD-3-Clause",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
    ],
)
