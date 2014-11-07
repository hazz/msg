import requests
import auth
import json
from base64 import standard_b64encode as b64e, standard_b64decode as b64d
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
    conversations = get("conversations/"+name)
    processed_conversations = [] 
    for (s, r, body, key1, key2) in conversations:
      if r == username:
        processed_conversations.append((s, r, decrypt_message(body, key1)))
      else:
        processed_conversations.append((s, r, decrypt_message(body, key2)))
    return processed_conversations

def decrypt_message(msg, key):
  key = auth.decrypt(b64d(key))
  return auth.aes_decrypt(b64d(msg), key)

# TODO:
# Duplicate key A
# Encrypt duplicate with sender's public key
def send_message(name, msg):
    keyA, body = auth.aes_encrypt(msg)
    body = b64e(body)
    recipient_key = key_for(name)
    if recipient_key is None:
      return False
    keyA2 = keyA
    keyA = b64e(auth.encrypt(keyA, recipient_key))
    keyA2 = b64e(auth.encrypt(keyA2, auth.public_key()))
    payload = {'sender': username, 'recipient': name, 'body': body, 'key': keyA, 'sender_key': keyA2}
    sig = b64e(str(auth.sign(auth.hash(username+name+body))))
    payload['signature'] = str(sig)
    keyB, payload = auth.aes_encrypt(json.dumps(payload))
    payload = b64e(payload)
    keyB = b64e(auth.encrypt(keyB, auth.server_key()))
    post("messages", {'key': keyB, 'payload': payload})

def key_for(name):
    res = get("users/"+name)
    if res is None:
      return None
    user, key = res
    return key

def set_username(name):
    global username
    username = name

def login():
    global cookie
    resp = post("login", {'username': username})
    if resp.status_code == 200:
      data = json.loads(resp.text)
      client_secret = b64d(data['client_secret'])
      secret = auth.decrypt(client_secret)
      sig = auth.sign(secret)
      resp = post("authorise", {'username': username, 'server_secret': data['server_secret'], 'signature': b64e(str(sig))})
      if resp.status_code == 200:
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
