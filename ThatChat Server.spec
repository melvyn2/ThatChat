# -*- mode: python -*-

import sys
import os

block_cipher = None

# noinspection PyUnresolvedReferences
a = Analysis([os.path.join('Src', 'Server.py')], pathex=['Src'])

# noinspection PyUnresolvedReferences
pyz = PYZ(a.pure, a.zipped_data)

# noinspection PyUnresolvedReferences
exe = EXE(pyz,
		a.scripts,
		a.binaries + [('msvcp100.dll', 'C:\\Windows\\System32\\msvcp100.dll', 'BINARY'),
			('msvcr100.dll', 'C:\\Windows\\System32\\msvcr100.dll', 'BINARY')]
		if sys.platform in ['windows', 'win32'] else a.binaries,
		a.zipfiles,
		a.datas,
		name='ThatChatServer',
		debug=False,
		strip=False,
		upx=True,
		console=True)
