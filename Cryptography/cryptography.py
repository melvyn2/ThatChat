import binascii
from Crypto import Random
from Crypto.Cipher import AES


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
        # tag = enc[-AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt(enc[AES.block_size:-AES.block_size])
        # integ = True
        # try:
        #     cipher.verify(enc[-AES.block_size:])
        # except ValueError:
        #     integ = False
        # return plaintext, integ
        return plaintext
