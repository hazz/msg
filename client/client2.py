import requests
import auth
import json
import base64
from os.path import isfile

SERVER = "http://localhost:5000/"

username = None
cookie = None

def get(path):
    return requests.get(SERVER+path, cookies=cookie).json()

def post(path, data):
    return requests.post(SERVER+path, cookies=cookie, data=data)

def conversations():
    return get("conversations")

def conversation(name):
    global username
    return [(s, r, auth.decrypt(base64.standard_b64decode(b))) if r == username else (s, r, '[encrypted]') for (s, r, b) in get("conversations/"+name)]

# TODO:
# encrypt body with recipient's public key
# sign hash(sender.recipient.body) with private key
# encrypt whole message with server's public key -- don't bother with this
def send_message(name, msg):
    body = base64.standard_b64encode(auth.encrypt(msg, key_for(name)))
    payload = {'sender': username, 'recipient': name, 'body': body}
    sig = auth.sign(auth.hash(username+name+body))
    payload['signature'] = str(sig)
    post("messages", payload)

def key_for(name):
    # get key from server
    user, key = get("users/"+name)
    return key

def set_username(name):
    global username
    username = name

def login():
    global cookie
    resp = post("login", {'username': username, 'signature': auth.sign(username)})
    cookie = resp.cookies

def register():
    global username
    key = auth.public_key().exportKey()
    post("register", {'username': username, 'public_key': key})

def generate_key():
    if isfile("key.pem"):
        print "delete or move key.pem first."
        return
    with open("key.pem", "w") as f:
        f.write(auth.generate_key())
