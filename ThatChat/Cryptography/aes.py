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

import binascii
from Cryptodome import Random
from Cryptodome.Cipher import AES


class AESCipher(object):

	def __init__(self, key):
		self.key = key[:16]

	def encrypt(self, raw):
		nonce = Random.new().read(AES.block_size)
		cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
		ciphertext, tag = cipher.encrypt_and_digest(raw)
		return binascii.b2a_hex(nonce + ciphertext + tag)

	def decrypt(self, enc):
		enc = binascii.a2b_hex(enc)
		nonce = enc[:AES.block_size]
		tag = enc[-AES.block_size:]
		cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
		plaintext = cipher.decrypt(enc[AES.block_size:-AES.block_size])
		integ = True
		try:
			cipher.verify(tag)
		except ValueError:
			integ = False
		return plaintext, integ
