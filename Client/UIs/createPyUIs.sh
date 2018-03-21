#!/usr/bin/env bash
cd "$(dirname ${BASH_SOURCE[0]})"
pyuic5 mainWindow.ui -o ../PyUIs/MainWindow.py
pyuic5 serverDialog.ui -o ../PyUIs/ServerDialog.py
pyuic5 usernameDialog.ui -o ../PyUIs/UsernameDialog.py