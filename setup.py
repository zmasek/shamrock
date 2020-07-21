#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script for Shamrock library."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["requests==2.21.0"]

test_requirements = ["vcrpy==2.0.1"]

setup(
    author="Zlatko Mašek",
    author_email="zlatko.masek@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="A Trefle API Integration.",
    install_requires=requirements,
    license="MIT license': 'License :: OSI Approved :: MIT License",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="shamrock",
    name="shamrock",
    packages=find_packages(include=["shamrock"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/zmasek/shamrock",
    version="0.0.2",
    zip_safe=False,
)
