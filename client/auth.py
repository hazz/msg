from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Signature import PKCS1_v1_5 as pk
from Crypto.Cipher import PKCS1_OAEP as oaep

keyfile = "key.pem"
server_public_key = "server.pub.pem"

def set_keyfile(filename):
    global keyfile
    keyfile = filename

def key():
    global keyfile
    with open(keyfile, "r") as f:
        return RSA.importKey(f.read())

def server_key():
    global server_public_key
    with open(server_public_key, "r") as f:
        return RSA.importKey(f.read())

def sign(msg):
    h = SHA256.new(msg)
    sig = pk.new(key()).sign(h)
    return sig

def verify(msg, sig, key):
   h = SHA256.new(msg)
   return pk.new(key).verify(h, sig)

def public_key():
    return key().publickey()

def generate_key():
    return RSA.generate(2048).exportKey()

def encrypt(msg, key):
    if not isinstance(key, RSA._RSAobj):
        key = RSA.importKey(key)
    return oaep.new(key).encrypt(msg)

def encrypt_for_server(msg):
    global server_key
    return oaep.new(server_key()).encrypt(msg)

def decrypt(msg):
    return oaep.new(key()).decrypt(msg)

def hash(data):
    hash = SHA256.new(data)
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

