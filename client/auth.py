from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256

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
    (sig, ) = key().sign(msg, 0)
    return sig

def public_key():
    return key().publickey()

def generate_key():
    return RSA.generate(2048).exportKey()

def encrypt(msg, key):
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
