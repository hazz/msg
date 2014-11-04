import curses
import client2 as cl
from random import random as rand
import sys

stdscr = None
cursor = 0

def setup(username, keyfile):
    cl.set_username(username)
    cl.auth.set_keyfile(keyfile)
    cl.login()

def line(y, text):
    global cursor
    if cursor == y:
        stdscr.addstr(y, 0, text, curses.A_STANDOUT)
    else:
        stdscr.addstr(y, 0, text)

def moveup():
    global cursor
    if cursor == 0:
        return
    else:
        cursor = cursor - 1

def show_conversation(name):
    global cursor, stdscr
    cursor = -1
    conv = cl.conversation(name)
    render_conversation(conv)
    stdscr.refresh()
    msg = ""
    while True:
        c = stdscr.getch()
        if c in (curses.KEY_ENTER, 10):
            if msg != "":
                cl.send_message(name, msg)
                msg = ""
            stdscr.clear()
            render_conversation(cl.conversation(name))
        else:
            if c in range(32, 127):
                msg += chr(c)
                stdscr.addch(chr(c))
            if c in (curses.KEY_BACKSPACE, 127, 13):
                msg = msg[0:len(msg) - 1]
                stdscr.delch()
                stdscr.refresh()
        stdscr.refresh()


def render_conversation(conv):
    for i, c in enumerate(conv):
        sender, recipient, body = c
        line(i, "%s:\t%s" % (sender, body))
    line(len(conv), "%s:\t" % (cl.username,))

def run(s):
    global stdscr, cursor
    convos = cl.conversations()
    stdscr = s
    while True:
        line(0, "Welcome to msg.")
        line(1, "Conversations:")
        for i, c in enumerate(convos):
            line(i + 2, c)
        stdscr.refresh()
        c = stdscr.getch()
        if c == curses.KEY_DOWN:
            cursor = cursor + 1
        if c == curses.KEY_UP:
            moveup()
        if c in (curses.KEY_ENTER, 10):
            stdscr.clear()         
            show_conversation(convos[cursor-2])


username = sys.argv[1] or 'alice'
keyfile = sys.argv[2] or 'key.pem'

setup(username, keyfile)
curses.wrapper(run)
