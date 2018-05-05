#!/usr/bin/env python2.7

#   Copyright (C) 2018 Melvyn Depeyrot
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
import pkgutil
import shutil
import sys
import fnmatch


def clean():
	delete(os.path.join('build', sys.platform))
	delete(os.path.join('bin', sys.platform))

	for r, d, f in os.walk('.'):
		for t in fnmatch.filter(f, '*.pyc'):
			delete(os.path.join(r, t))


def delete(obj):
	try:
		if os.path.isdir(obj):
			shutil.rmtree(obj)
		else:
			os.remove(obj)
	except OSError as e:
		if e.errno != 2:
			print(e)


action = sys.argv[1].lower() if len(sys.argv) >= 2 else None

if action == 'build':
	try:
		from PyInstaller.__main__ import run as freeze
		if sys.argv[2].lower() == 'client':
			clean()
			freeze(['--distpath', os.path.join('bin', sys.platform), '--workpath', os.path.join('build', sys.platform),
				'ThatChat Client.spec'])
		elif sys.argv[2].lower() == 'server':
			clean()
			freeze(['--distpath', os.path.join('bin', sys.platform), '--workpath', os.path.join('build', sys.platform),
				'ThatChat Server.spec'])
		elif sys.argv[2].lower() == 'all':
			clean()
			freeze(['--distpath', os.path.join('bin', sys.platform), '--workpath', os.path.join('build', sys.platform),
				'ThatChat Client.spec'])
			freeze(['--distpath', os.path.join('bin', sys.platform), '--workpath', os.path.join('build', sys.platform),
				'ThatChat Server.spec'])
		else:
			print('Usage: {0} build <program>\nWhere progam is \'client\', \'server\', or \'all\'.'.format(sys.argv[0]))
			sys.exit()
		print('You can find your built executable(s) in the \'bin' + os.sep + sys.platform + '\' directory.')
	except IndexError:
		print('Usage: {0} build <program>\nWhere progam is \'client\', \'server\', or \'all\'.'.format(sys.argv[0]))
	except ImportError:
		print('PyInstaller is missing.')

elif action == 'install':
	try:
		if sys.argv[2].lower() == 'Server':
			print('Currently (and for the forseeable future), installing the server will not be supported.')
			sys.exit()
		elif sys.argv[2].lower() != 'client':
			print('Install-able programs: \'client\'.')
			sys.exit()
		if sys.platform == 'darwin':
			if not os.path.isdir(os.path.join('dist', 'ThatChat Client.app')):
				print('You must build the program first, like so:\n    {0} build <program>'.format(sys.argv[0]))
				sys.exit()
			if len(sys.argv) == 4:
				installdir = os.path.expanduser(os.path.join(('~' if sys.argv[3] == '--user' else os.sep),
					'Applications', 'ThatChat Client.app'))
			elif len(sys.argv) == 5:
				installdir = os.path.expanduser(os.path.join((sys.argv[4] if sys.argv[3] == '--installdir'
					else (os.sep, 'Applications')), 'ThatChat Client.app'))
			else:
				installdir = os.path.join(os.sep, 'Applications', 'ThatChat Client.app')
			if os.path.isdir(installdir):
				update = raw_input('You already have a copy of the ThatChat client at {0}. '
					'Would you like to remove it and continue? (y/n) '.format(installdir))
				if update == 'y':
					delete(installdir)
				else:
					print('Aborted.')
					sys.exit()
			shutil.copytree(os.path.join('dist', 'ThatChat Client.app'), installdir)
			print('The ThatChat Client application bundle has been installed in the directory {0}'
				' under the name \'ThatChat Client.app\'.'.format(installdir))
		elif 'linux' in sys.platform:
			if not os.path.isfile(os.path.join('dist', 'ThatChat')):
				print('You must build the program first, like so:\n    {0} build'.format(sys.argv[0]))
				sys.exit()
			if len(sys.argv) == 4:
				installdir = os.path.expanduser(os.path.join('~' if '--user' in sys.argv[3] else
					(os.sep, 'usr', 'local'), 'bin'))
			if len(sys.argv) == 5:
				installdir = os.path.expanduser(os.path.join(sys.argv[4] if sys.argv[3] == '--installdir' else
					(os.sep, 'usr', 'local', 'bin')))
			else:
				installdir = os.path.join(os.sep, 'usr', 'local', 'bin')
			shutil.copy(os.path.join('dist', 'ThatChat'), os.path.join(os.sep, 'usr', 'local', 'bin'))
			print('The ThatChat Client has been installed in the directory {0} under the name \'ThatChat\'.'.format(installdir))
			if sys.argv[3] == '--user':
				print('Make sure that \'~/bin\' is in your PATH.')

		elif sys.platform in ['windows', 'win32']:
			print('Not fully developed yet. \'{0} build <program>\' will build the executable and put it in the '
				'\'dist\' directory.'.format(sys.argv[0]))
		else:
			print('Unrecognized platform.')
	except IndexError:
		print('Install-able programs: \'client\'.')
		sys.exit()


elif action == 'run':
	try:
		if sys.argv[2].lower() == 'client':
			from ThatChat.Client import main
			main()
		elif sys.argv[2].lower() == 'server':
			from ThatChat.Server import main
			try:
				main(sys.argv[3])
			except IndexError:
				main()
		else:
			print('Usage: {0} run <program>\nWhere progam is \'client\' or \'server\'.'.format(sys.argv[0]))
	except IndexError:
		print('Usage: {0} build <program>\nWhere progam is \'client\' or \'server\'.'.format(sys.argv[0]))

elif action == 'clean':
	clean()

elif action == 'deps':
	missing = []
	deps = {'pycryptodomex': 'Cryptodome', 'nclib': 'nclib', 'PyInstaller': 'PyInstaller', 'twisted': 'twisted',
				'pyyaml': 'yaml', 'pyDH': 'pyDH', 'urllib3': 'urllib3', 'cryptography': 'cryptography', 'idna': 'idna',
				'certifi': 'certifi', 'pyopenssl': 'OpenSSL', 'service-identity': 'service_identity'}
	installed_packages = [x[1] for x in list(pkgutil.iter_modules())]
	for i in deps.keys():
		if deps[i] not in installed_packages:
			missing.append(i)
		if i == 'setuptools':
			import setuptools
			if setuptools.__version__ < '39':
				missing.append(i)
		elif i == 'PyInstaller' and i not in missing:
			import PyInstaller
			if PyInstaller.__version__[:8] != '3.4.dev0':
				missing.append(i)
	if len(missing) > 0:
		print('You are missing or need to upgrade/patch the following: ' + ', '.join(missing))
		if '-y' in sys.argv or raw_input('Install them or it? (y/n) ') == 'y':
			to_install = ['https://github.com/bjones1/pyinstaller/archive/pyqt5_fix_cleaned.zip' if x == 'PyInstaller'
				else ('' if x == 'PyQt5' else x) for x in missing]
			try:
				import pip
				# noinspection PyUnresolvedReferences
				pip.main(['install', '--upgrade'] + to_install)
			except AttributeError:
				try:
					# noinspection PyProtectedMember
					import pip._internal
					# noinspection PyProtectedMember
					pip._internal.main(['install', '--upgrade'] + to_install)
				except ImportError:
					print('Pip is missing.')
					sys.exit(1)
			except ImportError:
				print('Pip is missing.')
				sys.exit(1)
			try:
				import PyQt5
			except ImportError:
				print('PyQt5 must still be installed manually.')
			sys.exit(0)
		else:
			print('Aborted.')
			sys.exit(0)

	print('You have all dependencies installed!')

else:
	print('Invalid option\nPossible options: build, install [--user], install --installdir <installdir>,'
			' run <program>, clean, deps [-y]')
