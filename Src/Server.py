# See LISENCE file for legal information

import time
import sys
import pyDH
from Cryptography import crypto

from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
import twisted.internet.error


class ChatHandler(LineReceiver):

	def __init__(self, users):
		self.users = users
		self.name = None
		self.tdelay = 0
		self.state = 0

	def sendMsg(self, text, header='MESG'):
		self.transport.write('/' + header + self.aes.encrypt(text) + header + '/\r\n')

	def sendCmd(self, cmd):
		self.transport.write('/' + cmd + '\r\n')

	def connectionMade(self):
		self.transport.write('/HELO\r\n')

	def connectionLost(self, reason):
		for name, protocol in self.users.iteritems():
			if protocol != self:
				self.sendMsg(self.name, 'DSCT')
		if self.name in self.users:
			del self.users[self.name]

	def lineReceived(self, line):
		if self.state == 0:
			if line == '/REDY':
				self.dh = pyDH.DiffieHellman()
				self.dh_pubkey = self.dh.gen_public_key()
				self.transport.write('/DHPK' + str(self.dh_pubkey) + 'DHPK/\r\n')
				self.state = 3
		elif self.state == 3:
			if line[:5] == '/DHPK' and line[-5:] == 'DHPK/':
				self.dh_sharedkey = self.dh.gen_shared_key(long(line[5:-5]))
				self.aes = crypto.AESCipher(self.dh_sharedkey)
				self.state = 1
		elif self.state == 1:
			if line[:5] == '/UNST' and line[-5:] == 'UNST/':
				username, integ = self.aes.decrypt(line[5:-5])
				if username in self.users:
					self.sendCmd('UNTK')
					return
				if (not username.replace(" ", "").isalnum()) or username.isspace() or (not username):
					self.sendCmd('UNIV')
					return
				self.name = username
				self.sendCmd('UNOK')
				self.users[username] = self
				for name, protocol in self.users.iteritems():
					if protocol != self:
						protocol.sendMsg(self.name, 'UNJD')
				self.state = 2
		elif self.state == 2:
			if line[:5] == '/MESG' and line[-5:] == 'MESG/':
				dmsg, integ = self.aes.decrypt(line[5:-5])
				if (not dmsg.isspace()) and dmsg:
					if self.tdelay > time.localtime(time.time())[4] * 100 + time.localtime(time.time())[5] - 0.75:
						self.sendCmd('/NSPM')
					else:
						for protocol in self.users.itervalues():
							protocol.sendMsg('<span style=\"color:' + ('#0000ff' if protocol == self else '#40FF00') +
								';\" >[{0}]<span style=\"color:#000000;\" > {1}'.format(self.name, dmsg))
					self.tdelay = time.localtime(time.time())[4] * 100 + time.localtime(time.time())[5]


class ChatFactory(Factory):

	def __init__(self, logfile=None):
		self.LogFile = logfile
		self.users = {}

	def buildProtocol(self, addr):
		return ChatHandler(self.users)


if len(sys.argv) > 2:
	print('''Usage: python {0} [server port]
Example: python {0} 500
The default port is 7000.'''.format(sys.argv[0]))
	sys.exit(0)
try:
	reactor.listenTCP(int(sys.argv[1]) if len(sys.argv) == 2 else 7000, ChatFactory(None))
	reactor.run()

except ValueError:
	print('Port should be an integer.')

except twisted.internet.error.CannotListenError:
	print('''Could not bind to port {0}.
Try running as root/with sudo, or check if other procceses are using that port.'''
		.format(sys.argv[1] if len(sys.argv) == 2 else 7000))
	sys.exit(1)

except Exception as e:
	print(e)
	sys.exit(2)
