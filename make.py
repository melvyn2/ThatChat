#!/usr/bin/env python2.7

import os
import shutil
import sys
import fnmatch


def clean():
	delete('build')
	delete('bin' + sys.platform)
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
				'PyChat Client.spec'])
		elif sys.argv[2].lower() == 'server':
			clean()
			freeze(['--distpath', os.path.join('bin', sys.platform), '--workpath', os.path.join('build', sys.platform),
				'PyChat Server.spec'])
		elif sys.argv[2].lower() == 'all':
			clean()
			freeze(['--distpath', os.path.join('bin', sys.platform), '--workpath', os.path.join('build', sys.platform),
				'PyChat Client.spec'])
			freeze(['--distpath', os.path.join('bin', sys.platform), '--workpath', os.path.join('build', sys.platform),
				'PyChat Server.spec'])
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
			if not os.path.isdir(os.path.join('dist', 'PyChat Client.app')):
				print('You must build the program first, like so:\n    {0} build <program>'.format(sys.argv[0]))
				sys.exit()
			if len(sys.argv) == 4:
				installdir = os.path.expanduser(os.path.join(('~' if sys.argv[3] == '--user' else os.sep),
					'Applications', 'PyChat Client.app'))
			elif len(sys.argv) == 5:
				installdir = os.path.expanduser(os.path.join((sys.argv[4] if sys.argv[3] == '--installdir'
					else (os.sep, 'Applications')), 'PyChat Client.app'))
			else:
				installdir = os.path.join(os.sep, 'Applications', 'PyChat Client.app')
			if os.path.isdir(installdir):
				update = raw_input('You already have a copy of the PyChat client at {0}. '
					'Would you like to remove it and continue? (y/n) '.format(installdir))
				if update == 'y':
					delete(installdir)
				else:
					print('Aborted.')
					sys.exit()
			shutil.copytree(os.path.join('dist', 'PyChat Client.app'), installdir)
			print('The PyChat Client application bundle has been installed in the directory {0}'
				' under the name \'PyChat Client.app\'.'.format(installdir))
		elif 'linux' in sys.platform:
			if not os.path.isfile(os.path.join('dist', 'PyChat')):
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
			shutil.copy(os.path.join('dist', 'PyChat'), os.path.join(os.sep, 'usr', 'local', 'bin'))
			print('The PyChat Client has been installed in the directory {0} under the name \'PyChat\'.'.format(installdir))
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
			from Src.Client import main
			main()
		elif sys.argv[2].lower() == 'server':
			from Src.Server import main
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
	deps = ['Cryptodomex', 'PyQt5', 'nclib', 'PyInstaller', 'Twisted']
	import importlib
	for i in deps:
		try:
			importlib.import_module('Cryptodome' if i == 'Cryptodomex' else ('twisted' if i == 'Twisted' else i))
		except ImportError:
			missing.append(i)
	if len(missing) > 0:
		print('You are missing the following: ' + ', '.join(missing))
		if '-y' in sys.argv or raw_input('Install them or it? (y/n) ') == 'y':
			import pip
			to_install = ['https://github.com/bjones1/pyinstaller/archive/pyqt5_fix_cleaned.zip' if x == 'PyInstaller'
				else ('' if x == 'PyQt5' else x) for x in missing]
			pip.main(['install'] + to_install)
			if 'PyQt5' in missing:
				print('PyQt5 must still be installed manually.')
			sys.exit(0)
		else:
			print('Aborted.')
			sys.exit(0)
	try:
		import PyInstaller
		if PyInstaller.__version__[:8] != '3.4.dev0':
			print('Your version of PyInstaller isn\'t patched for PyQt5 or isn\'t latest one.')
			if '-y' in sys.argv or raw_input('Fix it? (y/n) ') == 'y':
				import pip
				pip.main(['uninstall', 'PyInstaller', '-y'])
				pip.main(['install', 'https://github.com/bjones1/pyinstaller/archive/pyqt5_fix_cleaned.zip'])
				sys.exit(0)
			else:
				print('Aborted.')
				sys.exit(0)
	except IndexError:
		pass
	print('You have all dependencies installed!')

else:
	print('Invalid option\nPossible options: build, install, install --user, install --installdir <installdir> run, clean,'
		' deps [-y]')
