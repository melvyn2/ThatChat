# -*- mode: python -*-

#   Copyright (C) 2018  melvyn2
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

import sys
import os

block_cipher = None

# noinspection PyUnresolvedReferences
a = Analysis([os.path.join('ThatChat', 'Client.py')], pathex=['ThatChat'])

# noinspection PyUnresolvedReferences
pyz = PYZ(a.pure, a.zipped_data)

# noinspection PyUnresolvedReferences
exe = EXE(pyz,
		a.scripts,
		a.binaries + [('msvcp100.dll', 'C:\\Windows\\System32\\msvcp100.dll', 'BINARY'),
			('msvcr100.dll', 'C:\\Windows\\System32\\msvcr100.dll', 'BINARY')]
		if sys.platform == 'win32' else a.binaries,
		a.zipfiles,
		a.datas,
		name='ThatChat' + ('.exe' if sys.platform == 'win32' else ''),
		debug=False,
		strip=False,
		upx=True,
		runtime_tmpdir=None,
		console=False)

if sys.platform == 'darwin':
	# noinspection PyUnresolvedReferences
	app = BUNDLE(exe, name='ThatChat Client.app', icon=None)
