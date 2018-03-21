# See LISENCE file for legal information

from PyQt5 import QtCore, QtWidgets
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
	netcat.send('/' + header + aescipher.encrypt(str(linedit.text().encode('utf-8'))) + header + '/\r\n')
	linedit.clear()

class Window(QtWidgets.QMainWindow):
	resized = QtCore.pyqtSignal()

	def __init__(self, parent=None):
		super(Window, self).__init__(parent=parent)

	def resizeEvent(self, event):
		self.resized.emit()
		return super(Window, self).resizeEvent(event)

def resize(ui, window):
	ui.textEdit.resize(window.width() - 41, window.height() - (ui.lineEdit.height() + 67))
	ui.lineEdit.move(ui.lineEdit.x(), ui.textEdit.y() + 7 + ui.textEdit.height())
	ui.lineEdit.resize(window.width() - (ui.sendButton.width() + 40), 91)
	ui.sendButton.move((ui.lineEdit.width() + ui.lineEdit.x() + 5), ui.textEdit.y() + 3 + ui.textEdit.height())

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
					self.toappend.emit(plain.decode('utf-8'))
				except Exception as e:
					print(e)

	def stop(self):
		self.terminate()

def execAndClose(main, thread):
	exitcode = main.exec_()
	thread.stop()
	return exitcode


def main():

	app = QtWidgets.QApplication(sys.argv)
	serverDialog = QtWidgets.QDialog()
	usernameDialog = QtWidgets.QDialog()
	serverUi = server_dialog.Ui_Dialog()
	serverUi.setupUi(serverDialog)
	serverUi.buttonBox.rejected.connect(sys.exit)
	# QtCore.QObject.connect(serverUi.buttonBox, QtCore.SIGNAL(_fromUtf8('rejected()')), sys.exit)
	serverDialog.setFixedSize(serverDialog.size())
	usernameUi = username_dialog.Ui_Dialog()
	usernameUi.setupUi(usernameDialog)
	usernameUi.buttonBox.rejected.connect(sys.exit)
	# QtCore.QObject.connect(usernameUi.buttonBox, QtCore.SIGNAL(_fromUtf8('rejected()')), sys.exit)
	usernameDialog.setFixedSize(usernameDialog.size())
	ChatClientWindow = Window()
	mainUi = main_window.Ui_MainWindow()
	while True:
		serverDialog.exec_()
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
			nc = Netcat((HOST, PORT), verbose=False)
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
		usernameDialog.exec_()
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
	ChatClientWindow.resized.connect(lambda: resize(mainUi, ChatClientWindow))
	ChatClientWindow.show()
	running = True
	recieveThread = RecvThread(nc, aes)
	recieveThread.toappend.connect(lambda txt: mainUi.textEdit.append(txt))
	recieveThread.start()
	sys.exit(execAndClose(app, recieveThread))

main()
