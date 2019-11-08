#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages


def get_resources_data():
    result = []
    this_dir = os.path.dirname(os.path.realpath(__file__)) + "/ligm"
    for root, dirnames, filenames in os.walk(this_dir):
        for filename in filenames:
            result.append(os.path.join(os.path.relpath(root, this_dir),
                                        filename))
    return result


setup(
    name='ligm.spell',
    version='1.0.0',
    description='Spellchecker.',
    author='Vladimir Rukavishnikov',
    author_email='ligm74@inbox.ru',
    install_requires=[],
    packages=find_packages(),
    package_data={'': get_resources_data()},
    include_package_data=True,
    # url="-",
    license="MIT",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    platforms="any",
    long_description='Spellchecker.',
    # long_description=open(
    #    os.path.join(os.path.dirname(__file__), 'README.txt')).read(),
    entry_points={},
)

