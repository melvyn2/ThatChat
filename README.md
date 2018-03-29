# PyChat - Encrypted Python Chat

This a small python project for encrypted chat.


Requirements
------------
• [Python 2.7](https://www.python.org/)

• [Pycryptodome/Pycryptodomex](https://github.com/Legrandin/pycryptodome)

• [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5)

• [nclib](https://github.com/rhelmot/nclib)

• [pyDH](https://github.com/amiralis/pyDH)

• (For Building) [PyInstaller (with PyQt5 Fix)](https://github.com/pyinstaller/pyinstaller/pull/3233#issuecomment-362094587)


Known Issues
------------
Compeletly vulnerable to MITM (no authenticity checks)

PyQt5 fix for PyInstaller required for correctly building project (wont fix here). Click on the pyinstaller link and follow the instructions in the comment.