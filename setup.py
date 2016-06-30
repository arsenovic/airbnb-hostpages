#!/usr/bin/env python

from setuptools import setup, find_packages
from distutils.core import Extension

VERSION = '0.1'
LONG_DESCRIPTION = """
	generates a webpage for an air-bnb hosts with multiple listings
"""
setup(name='hostpages',
	version=VERSION,
	description='webpage generator for airbnb hosts',
	long_description=LONG_DESCRIPTION,
	author='alex arsenovic',
	author_email='alex@810lab.com',
	packages=find_packages(),
	install_requires = [
		'scrapy',
        'pyyaml',
        'distutils',
        'pandas',
        
		],
	package_dir={'hostpages':'hostpages'},
	
	)

