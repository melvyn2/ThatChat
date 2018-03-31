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


global program
global action

if str(sys.argv[1]).lower() in ['client', 'server']:
	program = str(sys.argv[1]).title()
elif str(sys.argv[1]).lower() == 'clean':
	action = 'clean'
else:
	print('Invaild program. Programs are: client, server')
	sys.exit()
action = sys.argv[2].lower() if len(sys.argv) >= 3 and (not action) else action

if action == 'build':
	pyinstallerPath = None
	if len(sys.argv) == 4:
		pyinstallerPath = sys.argv[3]
	else:
		for path in os.environ['PATH'].split(os.pathsep):
			if os.path.isfile(os.path.join(path, 'pyinstaller')):
				pyinstallerPath = path
				break
		if not pyinstallerPath:
			pyinstallerPath = raw_input("Path to bindir containing pyinstaller: ")

	clean()
	subprocess.call([os.path.join(pyinstallerPath, 'pyinstaller'), ('PyChat ' + program + '.spec')])

elif action == 'install':
	if program == 'Server':
		print('Currently (and for the forseeable future), installing the server will not be supported.')
	if sys.platform == 'darwin':
		if not os.path.isdir(os.path.join('dist', 'PyChat Client.app')):
			print('You must build the program first, like so:\n    {0} build'.format(sys.argv[0]))
			sys.exit()
		if len(sys.argv) == 4:
			installdir = os.path.expanduser(os.path.join(('~' if sys.argv[3] == '--user' else os.sep),
				'Applications', 'PyChat Client.app'))
		elif len(sys.argv) == 5:
			installdir = os.path.expanduser(os.path.join((sys.argv[4] if sys.argv[3] == '--installdir' else os.sep),
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
			print('You must build the program first, like so:\n    {0} build'.format(sys.argv[0]))
			sys.exit()
		if len(sys.argv) == 4:
			installdir = os.path.expanduser(os.path.join('~' if sys.argv[3] == '--user' else
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

	elif 'win' in sys.platform:
		print('Not fully developed yet. \'{0} build\' will build the executable and put it in the \'dist\' directory.'
			.format(sys.argv[0]))

elif action == 'run':
	subprocess.call(['python2.7', os.path.join('Src', (program + '.py'))] + sys.argv[3:])

elif action == 'clean':
	clean()

else:
	print 'Invalid option\nPossible options: build, install, install --user, install --installdir <installdir> run, clean'
