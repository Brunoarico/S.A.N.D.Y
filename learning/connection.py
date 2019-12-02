import socket
import sys

if(len(sys.argv) > 1):
    opt = sys.argv[1]
else:
    opt ='nothing'

sock = socket.socket()

host = "192.168.0.199"
port = 80

sock.connect((host, port))

message = opt+"\n"
sock.send(message.encode())

data = ""
c = ""

while(not c == '\n'):
    c = sock.recv(1).decode()
    data += c
    if(len(data) > 20): break

print(data)
