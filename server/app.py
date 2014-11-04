from flask import Flask, g, request, abort, session
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import json
import sqlite3
import auth
from base64 import standard_b64encode as b64e, standard_b64decode as b64d


DATABASE = './messages.sqlite'
app = Flask(__name__)
app.secret_key = 'Brl3lbHVQ11CWOL3E1hy'


# Database
def db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# TODO: store username in session

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
    print name
    print sig
    if authenticate(name, sig):
        session['username'] = name
        return "Success"
    else:
        abort(401)


@app.route("/users/<user>")
def user_key(user):
    return json.dumps(get_user(user))


@app.route("/messages", methods=['POST'])
def messages():
    (success, sender, recipient, body, key) = authenticate_message(request.form)
    if success:
        send_message(sender, recipient, body, key)
        return "Success"
    else:
        abort(300)


@app.route("/conversations")
def conversations():
    if 'username' not in session:
            abort(401)
    g.username = session['username']
    return json.dumps(get_conversations())


@app.route("/conversations/<name>")
def conversation(name):
    if 'username' not in session:
        abort(401)
    g.username = session['username']
    return json.dumps(get_conversation(name))


# App Logic
def register_user(name, pubkey):
    if get_user(name) is not None:
        return False
    db().execute("insert into users values (?,?)", (name, pubkey))
    db().commit()
    return True


def authenticate_message(form):
    print type(form['key'])
    keyB = auth.decrypt(b64d(form['key']))
    payload = b64d(form['payload'])
    payload = auth.aes_decrypt(payload, keyB)
    payload = json.loads(payload)
    sender, recipient, body, keyA, sig = payload['sender'], payload['recipient'], payload['body'], payload['key'], payload['signature']
    sender_user = get_user(sender)
    recipient_user = get_user(recipient)
    if not (sender_user and recipient_user):
        return (False,)
    (name, keystring) = sender_user
    pubkey = RSA.importKey(keystring)
    digest = SHA256.new(sender+recipient+body).hexdigest()
    sig = b64d(sig)
    if pubkey.verify(digest, (long(sig),)):
        return (True, sender, recipient, body, keyA)
    else:
        return (False,)


# TODO: sign hashes instead of raw usernames
def authenticate(name, sig):
    """Client sends name and signature of username. Verify signature with user's public key"""
    user = get_user(name)
    if user is None:
        print "User does not exist."
        return False
    (name, keystring) = user
    print "Found user %s" % (name,)
    pubkey = RSA.importKey(keystring)
    print pubkey.publickey().exportKey()
    test = pubkey.verify(str(name), (long(sig),))
    print test
    return test


def add_user(name, pubkey):
    db().execute("insert into users values (?,?)", (name, pubkey))


def get_user(name):
    return db().execute("select * from users where name =?", (name,)).fetchone()


def get_messages():
    messages = db().execute("select * from messages where recipient =?", (g.username,))
    return [{'sender':s, 'recipient':r, 'body':b, 'key':k} for (s,r,b,k) in messages.fetchall()]


def send_message(sender, recipient, body, key):
    print (sender, recipient, body)
    db().execute('INSERT INTO messages VALUES (?,?,?,?)', (sender, recipient, body, key))
    db().commit()


def get_conversations():
    conversations = db().execute("select distinct sender from messages where recipient =?", (g.username,)).fetchall()
    return [s for (s,) in conversations]

def get_conversation(name):
    return db().execute("select * from messages where \
                                (sender =:username and recipient =:othername) or \
                                (sender =:othername and recipient =:username)",
                        {'username': g.username, 'othername': name}).fetchall()

if __name__ == '__main__':
    app.run(debug=True)
