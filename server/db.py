import sqlite3

connection = None

def conn():
  global connection
  if connection is None:
    connection = sqlite3.connect("./messages.sqlite")
  return connection


def create_tables():
    cursor = conn().cursor()
    cursor.execute("DROP TABLE IF EXISTS messages")
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("CREATE TABLE messages (sender text, recipient text, body text, key text, sender_key text)")
    cursor.execute("CREATE TABLE users (name text, publickey text)")


def get_messages(recipient):
    cursor = conn().cursor()
    cursor.execute("select * from messages where recipient =?", (recipient,))
    return cursor.fetchall()


def send_message((sender, recipient, body, key, sender_key)):
    conn().execute('INSERT INTO messages VALUES (?,?,?,?,?)', (sender, recipient, body, key, sender_key))
    conn().commit()

def add_user(name, key):
    conn().execute("INSERT INTO users VALUES (?,?)", (name, key))
    conn().commit()
    
def get_user(name):
    res = conn().execute("select * from users where name =?", (name,)).fetchone()
    return res

def get_conversations(name):
    conversations = conn().execute("select distinct sender from messages where recipient =?", (name,)).fetchall()
    return [s for (s,) in conversations]

def get_conversation(uname, name):
    return conn().execute("select * from messages where \
                                (sender =:username and recipient =:othername) or \
                                (sender =:othername and recipient =:username)",
                        {'username': uname, 'othername': name}).fetchall()



def close():
    conn().commit()
    conn().close()
