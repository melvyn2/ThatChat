# PyChat - Encrypted Python Chat [![Build Status - Travis CI](https://travis-ci.org/melvyn2/PyChat.svg?branch=master)](https://travis-ci.org/melvyn2/PyChat) [![Build Status - Appveyor](https://ci.appveyor.com/api/projects/status/github/melvyn2/pychat?svg=true)](https://ci.appveyor.com/api/projects/status/github/melvyn2/pychat?svg=true)

This a small python project for encrypted chat.


Requirements
------------
• [Python 2.7](https://www.python.org/)

• [PycryptodomeX](https://github.com/Legrandin/pycryptodome) : `pip install pycryptodomex`

• [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5) for the client

• [nclib](https://github.com/rhelmot/nclib) for the client

• [pyDH](https://github.com/amiralis/pyDH)

• PyInstaller (with PyQt5 Fix) : `pip install https://github.com/bjones1/pyinstaller/archive/pyqt5_fix_cleaned.zip` for building

• [Twisted](http://twistedmatrix.com/)


Known Issues
------------
Compeletly vulnerable to MITM (no authenticity checks); Server signing coming soon.

PyQt5 fix for PyInstaller required for correctly building project (wont fix here). Click on the pyinstaller link and follow the instructions in the comment.
