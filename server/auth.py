from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.Cipher import AES

keyfile = "key.pem"

def set_keyfile(filename):
    global keyfile
    keyfile = filename

def key():
    global keyfile
    with open(keyfile, "r") as f:
        return RSA.importKey(f.read())

def sign(msg):
    (sig, ) = key().sign(msg, 0)
    return sig

def public_key():
    return key().publickey()

def generate_key():
    return RSA.generate(2048).exportKey()

def encrypt(msg, key):
    if not isinstance(key, RSA._RSAobj):
        key = RSA.importKey(key)
    (res,) = key.encrypt(msg, 0)
    return res

def encrypt_for_server(msg):
    global server_key
    (res,) = server_key().encrypt(msg, 0)
    return res

def decrypt(msg):
    return key().decrypt(msg)

def hash(data):
    hash = SHA256.new()
    hash.update(data)
    return hash.hexdigest()

def aes_encrypt(data):
    key = Random.new().read(AES.block_size)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return (key, iv+cipher.encrypt(data))

def aes_decrypt(data, key):
    iv = data[0:AES.block_size]
    data = data[AES.block_size:len(data)]
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return cipher.decrypt(data)

def generate_secret():
    return Random.new().read(40)

def verify(key, data, sig):
    if not isinstance(key, RSA._RSAobj):
      key = RSA.importKey(key)
    return key.verify(data, (long(sig),))

