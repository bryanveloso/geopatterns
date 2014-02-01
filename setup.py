#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from setuptools import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


setup(
    name='geopatterns',
    version='0.0.1',
    description='Generative background images.',
    long_description=open('README.md').read(),
    author='Bryan Veloso',
    author_email='bryan@revyver.com',
    url='https://github.com/bryanveloso/geopatterns',
    py_modules=['geopatterns'],
    install_requires=['colour'],
    license='MIT',
)
