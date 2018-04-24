#!/usr/bin/env python2.7

#   Copyright (C) 2018  Melvyn Depeyrot
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from setuptools import setup
from setuptools import find_packages


def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
	name='ThatChat',
	version='0.1.2',
	packages=find_packages(),
	url='https://github.com/melvyn2/ThatChat',
	license='GPLv3',
	author='Melvyn Depeyrot',
	author_email='melvyn.depeyrot@gmail.com',
	long_description=read('README.md'),
	description='Encrypted chat, in python.',
	install_requires=['nclib', 'pyDH', 'PyYAML', 'certifi', 'urllib3', 'twisted', 'pycryptodomex']
)
