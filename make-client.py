#!/usr/bin/env python2.7

import os
import shutil
import subprocess
import sys
import fnmatch

def clean():
	delete('build')
	delete('dist')
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


action = sys.argv[1] if len(sys.argv) >= 2 else None

if action == 'build':
	pyinstallerPath = None
	if len(sys.argv) == 3:
		pyinstallerPath = sys.argv[2]
	else:
		for path in os.environ['PATH'].split(os.pathsep):
			if os.path.isfile(os.path.join(path, 'pyinstaller')):
				pyinstallerPath = path
				break
		if not pyinstallerPath:
			pyinstallerPath = raw_input("Path to bindir containing pyinstaller: ")

	clean()
	subprocess.call([os.path.join(pyinstallerPath, 'pyinstaller'), 'PyChat Client.spec'])

elif action == 'install':
	if sys.platform == 'darwin':
		if not os.path.isdir(os.path.join('dist', 'PyChat Client.app')):
			print('You must build the program first, like so:\n    ./make-client.py build')
			sys.exit()
		if len(sys.argv) == 3:
			installdir = os.path.expanduser(os.path.join(('~' if sys.argv[2] == '--user' else os.sep),
				'Applications', 'PyChat Client.app'))
		elif len(sys.argv) == 4:
			installdir = os.path.expanduser(os.path.join((sys.argv[3] if sys.argv[2] == '--installdir' else os.sep),
				'Applications', 'PyChat Client.app'))
		else:
			installdir = os.path.join(os.sep, 'Applications', 'PyChat Client.app')
		if os.path.isdir(installdir):
			update = raw_input('You already have a copy of the PyChat client in {0}. '
				'Would you like to remove it and continue? (y/n)')
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
			print('You must build the program first, like so:\n    ./make-client.py build')
			sys.exit()
		if len(sys.argv) == 3:
			installdir = os.path.expanduser(os.path.join('~' if sys.argv[2] == '--user' else
				(os.sep, 'usr', 'local'), 'bin'))
		if len(sys.argv) == 4:
			installdir = os.path.expanduser(os.path.join(sys.argv[3] if sys.argv[2] == '--installdir' else
				(os.sep, 'usr', 'local', 'bin')))
		else:
			installdir = os.path.join(os.sep, 'usr', 'local', 'bin')
		shutil.copy(os.path.join('dist', 'PyChat'), os.path.join(os.sep, 'usr', 'local', 'bin'))
		print('The PyChat Client has been installed in the directory {0} under the name \'PyChat\'.'.format(installdir))
		if sys.argv[2] == '--user':
			print('Make sure that \'~/bin\' is in your PATH.')

	elif sys.platform == 'windows':
		print('Not fully developed yet. \'make.py build\' will build the executable and put it in the \'dist\' directory.')

elif action == 'run':
	subprocess.call(['python2.7', 'Src/Client.py'] + sys.argv[2:])

elif action == 'clean':
	clean()

else:
	print 'Invalid option\nPossible options: build, install, install --user, install --installdir <installdir> run, clean'
