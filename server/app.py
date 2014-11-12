from flask import Flask, g, request, abort, session
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import json
import sqlite3
import auth
import db
import logging
from base64 import standard_b64encode as b64e, standard_b64decode as b64d

DATABASE = './messages.sqlite'
app = Flask(__name__)
app.secret_key = 'Brl3lbHVQ11CWOL3E1hy'


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Routes
@app.route("/")
def index():
    return "msg"

@app.route("/register", methods=["POST"])
def register():
    name = request.form['username']
    app.logger.info("REGISTER: %s" % (name))
    pubkey = request.form['public_key']
    success = register_user(name, pubkey)
    if not success:
        app.logger.warn("User %s already exists - cannot register" % (name))
        abort(409)
    app.logger.info("User %s successfully registered" % (name))
    return "Success"


@app.route("/login", methods=["POST"])
def login():
    name = request.form['username']
    app.logger.info("LOGIN: %s" % (name))
    client_key = key_for(name)
    if client_key is None:
        app.logger.warn("No key exists for user %s. User may not be registered." % name)
        abort(401)
    secret = auth.generate_secret()
    p1 = auth.encrypt(secret, client_key)
    p2 = auth.encrypt(secret, auth.key())
    return json.dumps({'client_secret': b64e(p1), 'server_secret': b64e(p2)})

@app.route("/authorise", methods=["POST"])
def login2():
    name = request.form['username']
    p2 = request.form['server_secret']
    sig = request.form['signature']
    server_secret = auth.decrypt(b64d(p2))
    genuine = auth.verify(key_for(name), server_secret, b64d(sig))
    if genuine:
        session['username'] = name
        app.logger.info("%s successfully logged in" % (name,))
        return "Success"
    else:
        abort(401)

@app.route("/users/<user>")
def user_key(user):
    return json.dumps(db.get_user(user))


@app.route("/messages", methods=['POST'])
def messages():
    (success, msg) = authenticate_message(request.form)
    if success:
        db.send_message(msg)
        return "Success"
    else:
        abort(300)


@app.route("/conversations")
def conversations():
    if 'username' not in session:
            abort(401)
    g.username = session['username']
    res = db.get_conversations(g.username)
    app.logger.info(res)
    return json.dumps(res)


@app.route("/conversations/<name>")
def conversation(name):
    if 'username' not in session:
        abort(401)
    g.username = session['username']
    return json.dumps(db.get_conversation(g.username, name))


# App Logic
def register_user(name, pubkey):
    if db.get_user(name) is not None:
        return False
    db.add_user(name, pubkey)
    return True


def authenticate_message(form):
    keyB = auth.decrypt(b64d(form['key']))
    payload = b64d(form['payload'])
    payload = auth.aes_decrypt(payload, keyB)
    payload = json.loads(payload)
    sender, recipient, body, keyA, sig, keyA2 = payload['sender'], payload['recipient'], payload['body'], payload['key'], payload['signature'], payload['sender_key']
    sender_user = db.get_user(sender)
    recipient_user = db.get_user(recipient)
    if not (sender_user and recipient_user):
        return (False,)
    digest = SHA256.new(sender+recipient+body).hexdigest()
    sig = b64d(sig)
    if auth.verify(key_for(sender), digest, sig):
        return (True, (sender, recipient, body, keyA, keyA2))
    else:
        return (False,())

def key_for(name):
    user = db.get_user(name)
    if user is None:
        return None
    _, key = user
    return key

if __name__ == '__main__':
    #handler = FileHandler("info.log")
    #handler.setLevel(
    app.run(debug=True)

