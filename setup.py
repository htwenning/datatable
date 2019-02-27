#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import sys


if sys.version_info[0] == 2:
    raise Exception('python3 required.')

install_requirements = [
    'SQLAlchemy==1.2.17',
    'sanic==18.12.0'
]

setup(
    name='Sanic_Sqlalchemy_DataTable',
    version='0.0.3',
    url='https://github.com/htwenning/datatable',
    license='MIT',
    author='wenning',
    author_email='ht.wenning@foxmail.com',
    description='datatable backend.',
    packages=['sanic_sa_datatable'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=install_requirements,
)
