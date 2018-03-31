# -*- mode: python -*-

import sys
import os

block_cipher = None


a = Analysis([os.path.join('Src', 'Server.py')],
			  pathex=['Src'])

pyz = PYZ(a.pure,
		  a.zipped_data,
		  cipher=block_cipher)
exe = EXE(pyz,
		  a.scripts,
		  #a.binaries + [('msvcp100.dll', 'C:\\Windows\\System32\\msvcp100.dll', 'BINARY'),
			#('msvcr100.dll', 'C:\\Windows\\System32\\msvcr100.dll', 'BINARY')]
		  #if sys.platform == 'win32' else
		  a.binaries,
		  a.zipfiles,
		  a.datas,
		  name=os.path.join('PyChatServer' + ('.exe' if win in sys.platform else '')),
		  debug=False,
		  strip=False,
		  upx=True,
		  runtime_tmpdir=None,
		  console=True )
