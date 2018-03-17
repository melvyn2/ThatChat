#!/usr/bin/env python -m
import time
import sys
import pyDH
from ..Cryptography import crypto

# from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
# from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
import twisted.internet.error


class ChatHandler(LineReceiver):

    def __init__(self, users):  # , logfile=None):
        self.users = users
        self.name = None
        self.tdelay = 0
        self.state = 0
        # if LogFile: self.logfile = logfile
        # else: self.logfile = None

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
        # self.log('%s lost connection' % self.name)
        if self.name in self.users:
            del self.users[self.name]

    # def log(self, msg):
    # 	if self.logfile: self.logfile.write(msg + '\r\n')

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
                username = self.aes.decrypt(line[5:-5])
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
                # self.log('%s joined.' % self.name)
                self.state = 2
        elif self.state == 2:
            if line[:5] == '/MESG' and line[-5:] == 'MESG/':
                dmsg = self.aes.decrypt(line[5:-5]).decode('utf8')
                if (not dmsg.isspace()) and dmsg:
                    if self.tdelay > time.localtime(time.time())[4] * 100 + time.localtime(time.time())[5] - 0.75:
                        self.sendCmd('/NSPM')
                    else:
                        for protocol in self.users.itervalues():
                            protocol.sendMsg('<span style=\"color:' + ('#0000ff' if protocol == self else '#40FF00') + ';\" >[%s]<span style=\"color:#000000;\" > %s' % (self.name, dmsg))
                    self.tdelay = time.localtime(time.time())[4] * 100 + time.localtime(time.time())[5]


class ChatFactory(Factory):

    def __init__(self, logfile=None):
        self.LogFile = logfile
        self.users = {}

    def buildProtocol(self, addr):
        return ChatHandler(self.users)  # , self.LogFile)


if len(sys.argv) < 2 or len(sys.argv) > 3:
    print('Usage: [sudo] python -m PyChat.Server <server port> [logfile]\r\nExample: sudo python -m PyChat.Server 7000\r\nYou must be in the directory one level above the PyChat folder for it to work.')
    sys.exit(0)
try:
    reactor.listenTCP(int(sys.argv[1]), ChatFactory(sys.argv[3] if len(sys.argv) == 3 else None))
    reactor.run()

except twisted.internet.error.CannotListenError:
    print('Could not bind to port %s. Try running as root/with sudo, or checking if other procceses are using that port.' % sys.argv[1])
    sys.exit(1)

except Exception as e:
    print(e)
    sys.exit(2)