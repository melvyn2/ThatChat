#!/usr/bin/env python2.7

import os
import fnmatch
import subprocess

for r, d, f in os.walk('.'):
	for t in fnmatch.filter(f, '*.ui'):
		subprocess.call(['python', '-m', 'PyQt5.uic.pyuic', os.path.abspath(os.path.join(r, t)), '-o',
			os.path.abspath(os.path.join(r, t)).replace('UIs', 'PyUIs').replace('.ui', '.py')])
