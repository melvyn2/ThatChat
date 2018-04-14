#   Copyright (C) 2018 melvyn2
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, version 3.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtCore, QtWidgets
import sys
import os
import yaml
from nclib import Netcat, NetcatError
import pyDH
from Cryptography import aes, rsa
from PyUIs import MainWindow, ServerDialog, SignatureWarnDialog, SignatureInvalidDialog, UsernameDialog


def send_mesg(netcat, textedit, aescipher, header='MESG'):
	netcat.send('/' + header + aescipher.encrypt(str(textedit.toPlainText().encode('utf-8'))) + header + '/\r\n')
	textedit.clear()


# noinspection PyArgumentList
class Window(QtWidgets.QMainWindow):
	resized = QtCore.pyqtSignal()

	def __init__(self, parent=None):
		super(Window, self).__init__(parent=parent)

	def resizeEvent(self, event):
		self.resized.emit()
		return super(Window, self).resizeEvent(event)


# noinspection PyArgumentList
class TextEnter(QtWidgets.QTextEdit):
	enterPressed = QtCore.pyqtSignal()

	def keyPressEvent(self, event):
		if event.key() == 16777220:
			self.enterPressed.emit()
		else:
			super(TextEnter, self).keyPressEvent(event)


def resize(ui, window):
	ui.textEdit.resize(window.width() - 41, window.height() - (ui.textEdit_2.height() + 67))
	ui.textEdit_2.move(ui.textEdit_2.x(), ui.textEdit.y() + 7 + ui.textEdit.height())
	ui.textEdit_2.resize(window.width() - (ui.sendButton.width() + 40), 91)
	ui.sendButton.move((ui.textEdit_2.width() + ui.textEdit_2.x() + 5), ui.textEdit.y() + 3 + ui.textEdit.height())


# noinspection PyArgumentList
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
					plain, integ = self.aescipher.decrypt(data[5:-5])
					self.toappend.emit(('' if integ else 'Corrupted/tampered') + plain.decode('utf-8'))
				except Exception as e:
					print(e)

	def stop(self):
		self.terminate()


def exec_close(run, thread):
	exitcode = run.exec_()
	thread.stop()
	return exitcode


# noinspection PyArgumentList
def main():
	app = QtWidgets.QApplication(sys.argv)
	server_dialog = QtWidgets.QDialog()
	username_dialog = QtWidgets.QDialog()
	server_ui = ServerDialog.Ui_Dialog()
	server_ui.setupUi(server_dialog)
	server_ui.lineEdit.setPlaceholderText('127.0.0.1' if '--dbg' in sys.argv else '73.223.92.4')
	server_ui.buttonBox.rejected.connect(sys.exit)
	server_dialog.setFixedSize(server_dialog.size())
	chat_client_window = Window()
	main_ui = MainWindow.Ui_MainWindow()
	while True:
		server_dialog.exec_()
		try:
			port = int(server_ui.lineEdit_2.text() if server_ui.lineEdit_2.text() != ''
				else server_ui.lineEdit_2.placeholderText())
		except ValueError:
			server_ui.label_3.setText('Invalid Port1')
			continue
		if port > 65535:
			server_ui.label_3.setText('Invalid Port!2')
			continue
		host = server_ui.lineEdit.text() if server_ui.lineEdit.text() != ''\
			else server_ui.lineEdit.placeholderText()
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

	buf = nc.recv_until('\r\n').replace('\r\n', '')[5:-5].decode('hex')
	if getattr(sys, 'frozen', False):
		sig_db_path = os.path.join((os.getenv('LOCALAPPDATA') if sys.platform in ['win32', 'windows']
			else os.path.expanduser('~')), '.PyChatSignatureDB.yml')
	else:
		sig_db_path = 'signature_db.yml'
	try:
		sig_db = yaml.load(open(sig_db_path).read())
	except IOError:
		import certifi
		import urllib3
		import urllib3.contrib.pyopenssl
		urllib3.contrib.pyopenssl.inject_into_urllib3()
		try:
			f = open(sig_db_path, 'w')
			f.write(urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
				.request('GET', 'https://raw.githubusercontent.com/melvyn2/ThatChat/master/Src/signature_db.yml').data)
			f.close()
			sig_db = yaml.load(open(sig_db_path).read())
		except urllib3.exceptions.MaxRetryError:
			sig_db = {}
	if host in sig_db.keys():
		if str(sig_db[host]) == buf:
			print('Public keys match.')
		else:
			print('Public keys don\'t match.')
			signature_warn_dialog = QtWidgets.QDialog()
			signature_warn_ui = SignatureWarnDialog.Ui_Dialog()
			signature_warn_ui.setupUi(signature_warn_dialog)
			signature_warn_ui.buttonBox.rejected.connect(sys.exit)
			signature_warn_dialog.setFixedSize(signature_warn_dialog.size())
			signature_warn_ui.label_3.setText(host + ':' + str(port))
			signature_warn_dialog.exec_()
			try:
				del sig_db[host]
			except KeyError:
				pass
			sig_db[host] = buf
			open(sig_db_path, 'w').write(yaml.dump(sig_db))
	else:
		print('Don\'t have public key for this server.')
		sig_db[host] = buf
		open(sig_db_path, 'w').write(yaml.dump(sig_db))
	pubkey = rsa.import_pem_key(sig_db[host])
	nc.send('/PKOK\r\n')

	dh = pyDH.DiffieHellman()
	dh_pubkey = dh.gen_public_key()
	buf = long(nc.recv_until('\r\n').replace('\r\n', '')[5:-5])
	sig = nc.recv_until('\r\n').replace('\r\n', '')[5:-5]
	if rsa.Verification(pubkey).verify(str(buf), sig.decode('hex')):
		print('DH signatures match.')
	else:
		print('DH signature invalid.')
		signature_invalid_dialog = QtWidgets.QDialog()
		signature_invalid_ui = SignatureInvalidDialog.Ui_Dialog()
		signature_invalid_ui.setupUi(signature_invalid_dialog)
		signature_invalid_ui.buttonBox.rejected.connect(sys.exit)
		signature_invalid_dialog.setFixedSize(signature_invalid_dialog.size())
		signature_invalid_dialog.exec_()
	dh_sharedkey = dh.gen_shared_key(buf)
	encryption = aes.AESCipher(dh_sharedkey)
	nc.send('/DHPK' + str(dh_pubkey) + 'DHPK/\r\n')
	print('Completed DH handshake.')

	username_ui = UsernameDialog.Ui_Dialog()
	username_ui.setupUi(username_dialog)
	username_ui.buttonBox.rejected.connect(sys.exit)
	username_dialog.setFixedSize(username_dialog.size())
	while True:
		username_dialog.exec_()
		try:
			nc.send('/UNST' + encryption.encrypt(str(username_ui.lineEdit.text())) + 'UNST/\r\n')
		except UnicodeEncodeError:
			username_ui.label_2.setText('Unicode is not supported in usernames!')
			continue
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
	orig_geometry = main_ui.textEdit_2.geometry()
	main_ui.textEdit_2.deleteLater()
	main_ui.textEdit_2 = TextEnter(main_ui.centralwidget)
	main_ui.textEdit_2.setGeometry(orig_geometry)
	main_ui.textEdit_2.setObjectName("textEdit_2")
	chat_client_window.setCentralWidget(main_ui.centralwidget)
	main_ui.retranslateUi(chat_client_window)
	# noinspection PyCallByClass
	QtCore.QMetaObject.connectSlotsByName(chat_client_window)

	main_ui.sendButton.clicked.connect(lambda: send_mesg(nc, main_ui.textEdit_2, encryption))
	main_ui.textEdit_2.enterPressed.connect(lambda: send_mesg(nc, main_ui.textEdit_2, encryption))
	chat_client_window.resized.connect(lambda: resize(main_ui, chat_client_window))
	chat_client_window.setWindowTitle('ThatChat Client - {0}:{1}'.format(host, port))

	chat_client_window.show()
	recieve_thread = RecvThread(nc, encryption)
	recieve_thread.toappend.connect(main_ui.textEdit.append)
	recieve_thread.start()
	sys.exit(exec_close(app, recieve_thread))


if __name__ == '__main__':
	main()
