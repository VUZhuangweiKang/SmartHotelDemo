from Cryptodome.Cipher import AES
from Cryptodome import Random
from binascii import b2a_hex, a2b_hex, unhexlify
import random
import string

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * b'\0'


# Message Encryption Key Generator
def msg_key_gen(length, hasletters=True, hasdigits=True):
    if hasletters and hasdigits:
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
    if hasletters:
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))
    if hasdigits:
        return ''.join(random.choice(string.digits) for _ in range(length))


def cipher(key, data):
    if isinstance(key, str):
        key = key.encode('utf-8')
    key = pad(key)[:16]
    iv = Random.new().read(AES.block_size)
    mycipher = AES.new(key, AES.MODE_CBC, iv)
    if isinstance(data, str):
        data = pad(data.encode('utf-8'))
        ciphertext = iv + mycipher.encrypt(data)
    elif isinstance(data, bytes):
        data = pad(data)
        ciphertext = iv + mycipher.encrypt(data)
    else:
        ciphertext = None
    return b2a_hex(ciphertext)


def decrypt(key, data):
    if isinstance(key, str):
        key = key.encode('utf-8')
    key = pad(key)[:16]
    ciphertext = a2b_hex(data)
    iv = ciphertext[:AES.block_size]
    ciphertext = ciphertext[AES.block_size:len(ciphertext)]
    cryptor = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cryptor.decrypt(ciphertext)
    return plaintext.rstrip(b'\0')