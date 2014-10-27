import sqlite3

conn = sqlite3.connect('./messages.sqlite')


def create_tables():
    cursor = conn.cursor()
    cursor.execute('''DROP TABLE messages''')
    cursor.execute('''DROP TABLE users''')
    cursor.execute('''CREATE TABLE messages (sender text, recipient text, body text)''')
    cursor.execute('''CREATE TABLE users (name text, publickey text)''')


def get_messages(recipient):
    cursor = conn.cursor()
    cursor.execute("select * from messages where recipient =?", (recipient,))
    return cursor.fetchall()


def send_message(sender, recipient, body):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages VALUES (?,?,?)', (sender, recipient, body))


def close():
    conn.commit()
    conn.close()
