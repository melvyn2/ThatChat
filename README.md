ThatChat - Encrypted Python Chat
================================
[![Build Status - Travis CI](https://travis-ci.org/melvyn2/ThatChat.svg?branch=master)](https://travis-ci.org/melvyn2/ThatChat) [![Build Status - Appveyor](https://ci.appveyor.com/api/projects/status/github/melvyn2/thatchat?svg=true)](https://ci.appveyor.com/project/melvyn2/thatchat)
---
This a little project written in python 2 for encrypted chat.


Requirements
------------
• [Python 2.7](https://www.python.org/)

• [PycryptodomeX](https://github.com/Legrandin/pycryptodome) : `pip install pycryptodomex`

• [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5) for the client

• [nclib](https://github.com/rhelmot/nclib) for the client

• [pyDH](https://github.com/amiralis/pyDH)

• [PyInstaller](https://gitub.com/pyinstaller/pyinstaller): requires develop branch (`pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip`)

• [Twisted](http://twistedmatrix.com/) for the server


Building
--------
```bash
git clone https://github.com/melvyn2/ThatChat.git
cd ThatChat
./make.py deps
./make.py build all
```

Plannned Features
-----------------
• Rewrite in python3

• Password protected servers or chat rooms

• Different rooms on same server

• Able to be in multiple rooms at once through pyqt tabs

Test Server
-----------
A test server is availible at 73.223.92.4 running at port 7000