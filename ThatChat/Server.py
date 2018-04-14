#   Copyright (C) 2018  melvyn2
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import sys
import os

import pyDH

from Cryptodome.PublicKey import RSA

from Cryptography import aes, rsa

from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
import twisted.internet.error


# noinspection PyAbstractClass, PyMethodOverriding
class ChatHandler(LineReceiver):
	def __init__(self, users, key):
		self.users = users
		self.name = None
		self.tdelay = 0
		self.state = 0
		self.key = key
		self.signer = rsa.Verification(self.key)
		self.aes = None
		self.dh = None
		self.dh_pubkey = None
		self.dh_sharedkey = None

	def send_msg(self, text, header='MESG'):
		self.transport.write('/' + header + self.aes.encrypt(text) + header + '/\r\n')

	def send_cmd(self, cmd):
		self.transport.write('/' + cmd + '\r\n')

	def connectionMade(self):
		self.transport.write('/HELO\r\n')

	def connectionLost(self, reason):
		for protocol in self.users.values():
			if protocol != self:
				protocol.send_msg('<span style=\'color:#40FF00;\' >' + self.name + '<span style=\'color:#000000;\' > '
					+ ' disconnected.')
		if self.name in self.users:
			del self.users[self.name]

	def lineReceived(self, line):
		if self.state == 0:
			if line == '/REDY':
				self.transport.write('/PBKY' + str(self.key.publickey().exportKey())
					.encode('hex') + 'PBKY/\r\n')
				self.state = 1
		elif self.state == 1:
			if line == '/PKOK':
				self.dh = pyDH.DiffieHellman()
				self.dh_pubkey = self.dh.gen_public_key()
				self.transport.write('/DHPK' + str(self.dh_pubkey) + 'DHPK/\r\n')
				self.transport.write('/DHSG' + self.signer.sign(str(self.dh_pubkey)).encode('hex') + 'DHSG/\r\n')
				self.state = 2
		elif self.state == 2:
			if line[:5] == '/DHPK' and line[-5:] == 'DHPK/':
				self.dh_sharedkey = self.dh.gen_shared_key(long(line[5:-5]))
				self.aes = aes.AESCipher(self.dh_sharedkey)
				self.state = 3
		elif self.state == 3:
			if line[:5] == '/UNST' and line[-5:] == 'UNST/':
				username, integ = self.aes.decrypt(line[5:-5])
				if username in self.users:
					self.send_cmd('UNTK')
					return
				if (not username.replace(' ', '').isalnum()) or username.isspace() or (not username):
					self.send_cmd('UNIV')
					return
				self.name = username
				self.send_cmd('UNOK')
				self.users[username] = self
				for name, protocol in self.users.iteritems():
					if protocol != self:
						protocol.send_msg('<span style=\'color:#40FF00;\' >' + self.name + '<span style=\'color:#000000;\' > '
					+ ' joined.')
				self.state = 4
		elif self.state == 4:
			if line[:5] == '/MESG' and line[-5:] == 'MESG/':
				dmsg, integ = self.aes.decrypt(line[5:-5])
				if (not dmsg.isspace()) and dmsg:
					if self.tdelay > time.localtime(time.time())[4] * 100 + time.localtime(time.time())[5] - 0.75:
						self.send_cmd('/NSPM')
					else:
						for protocol in self.users.values():
							protocol.send_msg('<span style=\'color:' + ('#0000ff' if protocol == self else '#40FF00') +
								';\' >[{0}]<span style=\'color:#000000;\' > {1}'.format(self.name, dmsg))
					self.tdelay = time.localtime(time.time())[4] * 100 + time.localtime(time.time())[5]


class ChatFactory(Factory):

	def __init__(self, key=None):
		self.key = key
		self.users = {}

	def buildProtocol(self, addr):
		return ChatHandler(self.users, self.key)


# noinspection PyUnresolvedReferences
def main(port=7000, keypath=None):
	if not keypath:
		keypath = os.path.join((os.getenv('LOCALAPPDATA') if sys.platform in ['win32', 'windows']
			else os.path.expanduser('~')), '.PyChatServerKey.pem')
	if os.path.isfile(keypath):
		key = rsa.import_pem_key(open(keypath).read())
	else:
		key = RSA.generate(2048)
		open(keypath, 'wb').write(key.exportKey())

	try:
		reactor.listenTCP(int(port), ChatFactory(key))
		reactor.run()

	except ValueError:
		print('Port should be an integer.')

	except twisted.internet.error.CannotListenError:
		print('''Could not bind to port {0}.
Try running as root/with sudo, or check if other procceses are using that port.'''
			.format(port))
		sys.exit(1)

	except twisted.internet.error.ReactorNotRunning:
		sys.exit(0)

	except Exception as e:
		print(e)
		sys.exit(2)


if __name__ == '__main__':
	if len(sys.argv) > 3:
		print('''Usage: {0}{1} [server port] [private key file]
	Example: {0}{1} 5000
	The default port is 7000.'''.format(('' if getattr(sys, 'frozen', False) else 'python '), sys.argv[0]))
		sys.exit(0)

	if len(sys.argv) == 3:
		main(sys.argv[1], sys.argv[2])
	elif len(sys.argv) == 2:
		main(sys.argv[1])
	else:
		main()
