# See LISENCE file for legal information

from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import pss
from Cryptodome.Hash import SHA256


class Verification(object):
	def __init__(self, key):
		self.key = key

	def sign(self, text):
		sig = pss.new(self.key).sign(SHA256.new(text))
		return sig

	def verify(self, text, signature):
		try:
			pss.new(self.key).verify(SHA256.new(text), signature)
		except ValueError:
			return False
		return True


def import_pem_key(pemkey):
	from base64 import b64decode
	import os
	key64 = ''.join(pemkey.split(os.linesep)[1:-1])
	key_der = b64decode(key64)
	return RSA.importKey(key_der)
