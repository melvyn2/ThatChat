#-------------------------------------------------
#
# Project created by QtCreator 2018-01-28T17:39:22
#
#-------------------------------------------------

QT       += core gui

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = ChatClient
TEMPLATE = app


SOURCES += main.cpp\
        chatclientwindow.cpp

HEADERS  += chatclientwindow.h

FORMS    += main_window.ui \
    server_dialog.ui \
    username_dialog.ui
