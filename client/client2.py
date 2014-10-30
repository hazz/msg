import requests
import auth
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
    return get("conversations/"+name)

def send_message(name, msg):
    payload = {'sender': username, 'recipient': name, 'body': msg}
    post("messages", payload)

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
