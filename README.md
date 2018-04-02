# PyChat - Encrypted Python Chat [![Build Status](https://travis-ci.org/melvyn2/PyChat.svg?branch=master)](https://travis-ci.org/melvyn2/PyChat)

This a small python project for encrypted chat.


Requirements
------------
• [Python 2.7](https://www.python.org/)

• [Pycryptodome/Pycryptodomex](https://github.com/Legrandin/pycryptodome)

• [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5) for the client

• [nclib](https://github.com/rhelmot/nclib) for the client

• [pyDH](https://github.com/amiralis/pyDH)

• [PyInstaller (with PyQt5 Fix)](https://github.com/pyinstaller/pyinstaller/pull/3233#issuecomment-362094587) for building

• [Twisted](http://twistedmatrix.com/)


Known Issues
------------
Compeletly vulnerable to MITM (no authenticity checks); Server signing coming soon.

PyQt5 fix for PyInstaller required for correctly building project (wont fix here). Click on the pyinstaller link and follow the instructions in the comment.