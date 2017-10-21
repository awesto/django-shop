#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from setuptools import setup, find_packages
import sys
import shop
try:
    from pypandoc import convert
except ImportError:
    def convert(filename, fmt):
        if sys.version_info[0] < 3:
            with open(filename) as fd:
                return fd.read()
        else:
            with open(filename, encoding="utf-8") as fd:
                return fd.read()

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
]

setup(
    author="Jacob Rief",
    author_email="jacob.rief@gmail.com",
    name="django-shop",
    version=shop.__version__,
    description="A RESTful e-commerce framework based on Django",
    long_description=convert('README.md', 'rst'),
    url='http://www.django-shop.org/',
    license='BSD License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    packages=find_packages(exclude=['example', 'docs', 'testshop']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Django>=1.9.12,<1.11',
        'django-post-office>=3.0.0',
        'django-filer>=1.2.8',
        'django-ipware>=1.1.1',
        'django-fsm>=2.4.0',
        'django-fsm-admin>=1.2.4',
        'djangorestframework>=3.6.3',
        'django-angular>=1.1.2',
        'Django-Select2>=5.8.9',
        'django-rest-auth>=0.9.1',
        'django-admin-sortable2>=0.6.15',
        'django-formtools>=1.0',
        'djangocms-cascade>=0.14.1',
        'bs4>=0.0.1',
    ],
    # Note: this requires setuptools >= 18.0.
    extras_require={
        ':python_version<"3.4"': ['enum34'],
    },
)
