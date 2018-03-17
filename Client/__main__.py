#!/usr/bin/env python
from PyQt4 import QtCore, QtGui
import sys
from nclib import Netcat, NetcatError
import pyDH
from ..Cryptography import crypto
from PyUIs import main_window, server_dialog, username_dialog

try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	def _fromUtf8(s):
		return s


def sendMesg(netcat, linedit, aescipher, header='MESG'):
	netcat.send('/' + header + aescipher.encrypt(str(linedit.text())) + header + '/\r\n')
	linedit.clear()

def resize(ui, window):
	mainUi.textEdit.size().resize(ChatClientWindow.width() - 41, ChatClientWindow.height() - 183)
	mainUi.lineEdit.size().resize(ChatClientWindow.width() - 66, 91)

class RecvThread(QtCore.QThread):

	toappend = QtCore.pyqtSignal(str)

	def __init__(self, netcat, aescipher):
		QtCore.QThread.__init__(self)
		self.aescipher = aescipher
		self.netcat = netcat

	def run(self):
		while True:
			try:
				data = self.netcat.recv_until('\r\n').replace('\r\n', '')
			except NetcatError:
				print('Lost connection to server!')
				sys.exit(0)
			if data[:5] == '/MESG' and data[-5:] == 'MESG/':
				try:
					plain = self.aescipher.decrypt(data[5:-5])
					print plain
					self.toappend.emit(plain)
				except Exception as e:
					print(e)

	def stop(self):
		self.terminate()

def recvMesg(netcat, output, aescipher):
	toappend = QtCore.pyqtSignal(str)
	while True:
		try:
			data = netcat.recv_until('\r\n').replace('\r\n', '')
		except NetcatError:
			print('Lost connection to server!')
			sys.exit(0)
		print output
		if data[:5] == '/MESG' and data[-5:] == 'MESG/':
			try:
				plain = aescipher.decrypt(data[5:-5])
				print plain
				toappend.emit(plain)
			except Exception as e:
				print(e)

def execAndClose(main, thread):
	exitcode = main.exec_()
	thread.stop()
	return exitcode


if __name__ == '__main__':

	app = QtGui.QApplication(sys.argv)
	Dialog1 = QtGui.QDialog()
	Dialog2 = QtGui.QDialog()
	serverUi = server_dialog.Ui_Dialog()
	serverUi.setupUi(Dialog1)
	QtCore.QObject.connect(serverUi.buttonBox, QtCore.SIGNAL(_fromUtf8('rejected()')), sys.exit)
	usernameUi = username_dialog.Ui_Dialog()
	usernameUi.setupUi(Dialog2)
	QtCore.QObject.connect(usernameUi.buttonBox, QtCore.SIGNAL(_fromUtf8('rejected()')), sys.exit)
	ChatClientWindow = QtGui.QMainWindow()
	mainUi = main_window.Ui_MainWindow()
	while True:
		Dialog1.exec_()
		try:
			PORT = int(serverUi.lineEdit_2.text())
		except ValueError:
			serverUi.label_3.setText('Invalid Port!')
			continue
		if PORT > 65535:
			serverUi.label_3.setText('Invalid Port!')
			continue
		HOST = serverUi.lineEdit.text()
		try:
			nc = Netcat((HOST, PORT), verbose=True)
		except:
			serverUi.label_3.setText('Could not Connect!')
			continue
		break
	print('Connected to %s:%s' % (HOST, PORT))
	while True:
		buf = nc.recv_until('\r\n').replace('\r\n', '')
		if buf == '/HELO':
			break
	print('Server acknowledged connection.')
	nc.send('/REDY\r\n')
	dh = pyDH.DiffieHellman()
	dh_pubkey = dh.gen_public_key()
	buf = long(nc.recv_until('\r\n').replace('\r\n', '')[5:-5])
	dh_sharedkey = dh.gen_shared_key(buf)
	aes = crypto.AESCipher(dh_sharedkey)
	nc.send('/DHPK' + str(dh_pubkey) + 'DHPK/\r\n')
	print('Completed DH handshake.')

	while True:
		Dialog2.exec_()
		nc.send('/UNST' + aes.encrypt(str(usernameUi.lineEdit.text())) + 'UNST/\r\n')
		buf = nc.recv_until('\r\n').replace('\r\n', '')
		if buf == '/UNOK':
			break
		elif buf == '/UNTK':
			usernameUi.label_2.setText('Username Taken!')
			continue
		elif buf == '/UNIV':
			usernameUi.label_2.setText('Username Invalid!')
			continue

	print('Username is confirmed.')
	mainUi.setupUi(ChatClientWindow)
	mainUi.sendButton.clicked.connect(lambda: sendMesg(nc, mainUi.lineEdit, aes))
	mainUi.lineEdit.returnPressed.connect(lambda: sendMesg(nc, mainUi.lineEdit, aes))
	ChatClientWindow.show()
	running = True
	recieveThread = RecvThread(nc, aes)
	recieveThread.toappend.connect(lambda txt: mainUi.textEdit_2.append(txt))
	recieveThread.start()
	sys.exit(execAndClose(app, recieveThread))
