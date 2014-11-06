from flask import Flask, g, request, abort, session
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import json
import sqlite3
import auth
import db
from base64 import standard_b64encode as b64e, standard_b64decode as b64d


DATABASE = './messages.sqlite'
app = Flask(__name__)
app.secret_key = 'Brl3lbHVQ11CWOL3E1hy'


# Database
# def db():
#     db = getattr(g, '_database', None)
#     if db is None:
#         db = g._database = sqlite3.connect(DATABASE)
#     return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Routes
@app.route("/register", methods=["POST"])
def register():
    print request.form
    name = request.form['username']
    pubkey = request.form['public_key']
    success = register_user(name, pubkey)
    if not success:
        abort(409)
    return "Success"



@app.route("/login", methods=["POST"])
def login():
    name = request.form['username']
    sig = request.form['signature']
    if authenticate(name, sig):
        session['username'] = name
        print "%s successfully logged in." % (name,)
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
    return json.dumps(db.get_conversations(g.username))


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
    (name, keystring) = sender_user
    pubkey = RSA.importKey(keystring)
    digest = SHA256.new(sender+recipient+body).hexdigest()
    sig = b64d(sig)
    if pubkey.verify(digest, (long(sig),)):
        return (True, (sender, recipient, body, keyA, keyA2))
    else:
        return (False,())


# TODO: sign hashes instead of raw usernames
def authenticate(name, sig):
    """Client sends name and signature of username. Verify signature with user's public key"""
    user = db.get_user(name)
    if user is None:
        print "User does not exist."
        return False
    (name, keystring) = user
    pubkey = RSA.importKey(keystring)
    test = pubkey.verify(str(name), (long(sig),))
    return test


if __name__ == '__main__':
    app.run(debug=True)
