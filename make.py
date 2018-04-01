#!/usr/bin/env python2.7

import os
import shutil
import sys
import fnmatch
from PyInstaller.__main__ import run as freeze

def clean():
	delete('build')
	delete('bin')
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
		print('You can find your built executable(s) in the \'bin\' directory.')
	except IndexError:
		print('Usage: {0} build <program>\nWhere progam is \'client\', \'server\', or \'all\'.'.format(sys.argv[0]))

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

else:
	print 'Invalid option\nPossible options: build, install, install --user, install --installdir <installdir> run, clean'
