import auth
import client2 as cl2
import os

print "Generating private key.."
key = auth.generate_key()
with open("temp_key.pem", "w") as f:
  f.write(key)
cl2.auth.keyfile = "temp_key.pem"
success = False
while not success:
  cl2.username = raw_input("Pick a username: ")
  success = cl2.register()
  print "Attemping to register.."
  if not success:
    print "That username is taken."
print "Registered successfully."
print "Saving key as %s.pem" % (cl2.username)
with open(cl2.username+".pem", "w") as f:
    f.write(key)
os.remove("temp_key.pem")
print "DO NOT share this file with anyone"
print "You're all set. Run 'python client.py' or 'python cursestest.py' to chat"

