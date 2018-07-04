#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    "cyvcf2",
    "concise",
    "pyvcf",
    "dask",
    "joblib",
    "deepdish",
    "dask",
    "toolz",
    "cloudpickle",
    "kipoi",
    "scikit-learn",
    "openpyxl",
]

test_requirements = [
    "pytest",
    "virtualenv",
]
# TODO - require conda to be installed? - to create custom environments


setup(
    name='m_kipoi',
    version='0.0.1',
    description="Kipoi research code command-line tool",
    author="Kipoi team",
    author_email='...',
    url='https://github.com/kipoi/research-code',
    long_description=readme,
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        "develop": ["bumpversion",
                    "wheel",
                    "jedi",
                    "epc",
                    "pytest",
                    "pytest-pep8",
                    "pytest-cov"],
    },
    entry_points={'console_scripts': ['m_kipoi = m_kipoi.__main__:main']},
    license="MIT license",
    zip_safe=False,
    keywords=["model zoo", "deep learning",
              "computational biology", "bioinformatics", "genomics"],
    test_suite='tests',
    package_data={'m_kipoi': ['logging.conf']},
    tests_require=test_requirements
)
