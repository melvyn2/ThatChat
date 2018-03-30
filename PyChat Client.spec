# -*- mode: python -*-

import sys

block_cipher = None


a = Analysis(['Src/Client.py'],
             pathex=['./Src'],
			 binaries=[],
			 datas=[],
			 hookspath=[],
			 runtime_hooks=[],
			 excludes=[],
			 win_no_prefer_redirects=False,
			 win_private_assemblies=False,
			 cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
			 cipher=block_cipher)
exe = EXE(pyz,
		  a.scripts,
		  a.binaries + [('msvcp100.dll', 'C:\\Windows\\System32\\msvcp100.dll', 'BINARY'),
			('msvcr100.dll', 'C:\\Windows\\System32\\msvcr100.dll', 'BINARY')]
		  if sys.platform == 'win32' else a.binaries,
		  a.zipfiles,
		  a.datas,
		  name=os.path.join('PyChat' + ('.exe' if sys.platform == 'win32' else '')),
		  debug=False,
		  strip=False,
		  upx=True,
		  runtime_tmpdir=None,
		  console=True )

if sys.platform == 'darwin':
   app = BUNDLE(exe,
				name='PyChat Client.app',
				icon=None)
