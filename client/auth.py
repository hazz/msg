from Crypto.PublicKey import RSA

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
