msg
===
A toy encrypted chat system.

msg is an experiment in implementing a simple, secure, public key encrypted messaging system. It consists of a server written in Python and (any number of) clients that communicate with the server over HTTP. Messages are encrypted such that they can only be read by the sender and recipient, and (most, not yet all) communication with the server is encrypted. Messages are persisted on the server but the server has no way of obtaining the plaintext message contents. The encryption methods are broadly based on PGP, combining symmetric and asymmetric encryption in a mostly standard way. However there is absolutely no guarantee that the system is secure whatsoever. It has not been tested, reviewed, or even looked at by anyone with any extensive cryptography experience.

*THIS IS A TOY - DO NOT USE IT FOR ANYTHING IMPORTANT.*

Roadmap 
-------

1. Fully secure server communication.
2. Fully useable Python client.
3. Keybase integration
4. Native clients for iOS and OS X (Swift)
5. Windows/Linux clients

