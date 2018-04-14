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
