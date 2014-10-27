import client2 as cl2


def list_conversations():
    for c in cl2.conversations():
        print c
    main_loop()

def show_conversation(name):
    for (s, r, b) in cl2.conversation(name):
        print "%s:\t%s" % (s, b)
    conversation_loop(name)


def main_loop():
    cmd = raw_input('> ')
    if cmd == "list":
        return list_conversations()
    if cmd == "talk":
        recipient = raw_input("recipient: ")
        print "---"
        print "type to send messages. type :q to return to main menu"
        return show_conversation(recipient)
    if cmd == "exit":
        return exit()
    print "Unrecognised command."
    main_loop()


def conversation_loop(name):
    msg = None
    while msg != ':q':
        msg = raw_input('%s:\t' % cl2.username)
        cl2.send_message(name, msg)
    main_loop()


if __name__ == '__main__':
    uname = raw_input("username: ")
    cl2.set_username(uname)
    print "logging in..."
    cl2.login()
    print "Welcome to msg."
    print "Commands:"
    print "\tlist \t- list conversations"
    print "\ttalk \t- start/continue conversation"
    print "\texit \t- quit"
    main_loop()
