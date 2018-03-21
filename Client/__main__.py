# See LISENCE file for legal information

from PyQt5 import QtCore, QtWidgets
import sys
from nclib import Netcat, NetcatError
import pyDH
from ..Cryptography import crypto
from PyUIs import MainWindow, ServerDialog, UsernameDialog

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

def execAndClose(run, thread):
	exitcode = run.exec_()
	thread.stop()
	return exitcode


def main():

	app = QtWidgets.QApplication(sys.argv)
	server_dialog = QtWidgets.QDialog()
	username_dialog = QtWidgets.QDialog()
	server_ui = ServerDialog.Ui_Dialog()
	server_ui.setupUi(server_dialog)
	server_ui.buttonBox.rejected.connect(sys.exit)
	server_dialog.setFixedSize(server_dialog.size())
	username_ui = UsernameDialog.Ui_Dialog()
	username_ui.setupUi(username_dialog)
	username_ui.buttonBox.rejected.connect(sys.exit)
	username_dialog.setFixedSize(username_dialog.size())
	chat_client_window = Window()
	main_ui = MainWindow.Ui_MainWindow()
	while True:
		server_dialog.exec_()
		try:
			port = int(server_ui.lineEdit_2.text())
		except ValueError:
			server_ui.label_3.setText('Invalid Port!')
			continue
		if port > 65535:
			server_ui.label_3.setText('Invalid Port!')
			continue
		host = server_ui.lineEdit.text()
		try:
			nc = Netcat((host, port), verbose=False)
		except NetcatError:
			server_ui.label_3.setText('Could not Connect!')
			continue
		break
	print('Connected to {0}:{1}'.format(host, port))
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
		username_dialog.exec_()
		nc.send('/UNST' + aes.encrypt(str(username_ui.lineEdit.text())) + 'UNST/\r\n')
		buf = nc.recv_until('\r\n').replace('\r\n', '')
		if buf == '/UNOK':
			break
		elif buf == '/UNTK':
			username_ui.label_2.setText('Username Taken!')
			continue
		elif buf == '/UNIV':
			username_ui.label_2.setText('Username Invalid!')
			continue

	print('Username is confirmed.')
	main_ui.setupUi(chat_client_window)
	main_ui.sendButton.clicked.connect(lambda: sendMesg(nc, main_ui.lineEdit, aes))
	main_ui.lineEdit.returnPressed.connect(lambda: sendMesg(nc, main_ui.lineEdit, aes))
	chat_client_window.resized.connect(lambda: resize(main_ui, chat_client_window))
	chat_client_window.setWindowTitle('PyChat Client - {0}:{1}'.format(host, port))
	chat_client_window.show()
	recieve_thread = RecvThread(nc, aes)
	recieve_thread.toappend.connect(lambda txt: main_ui.textEdit.append(txt))
	recieve_thread.start()
	sys.exit(execAndClose(app, recieve_thread))


main()
