import socket

from SocketRDT import SocketRDT

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = b"Hello, World!"

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)





def main():
    sock = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP

    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print(addr)
    print(data)
    sock.shutdown()

    # Me contecto al IP+Puerto "estandar"
    #server = SocketRDT(addr=)
    # te envio N bytes
    # -------------->
    #puerto = server.init()

   # nuevoSocket = 
    # <------------
    # Joya, hablame a este puerto
    # Ok dale
    # * Creo el puerto *
    # 
    # 



'''
TCP client.py del libro de 

from socket import *
serverName = ’servername’
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
sentence = raw_input(’Input lowercase sentence:’)
clientSocket.send(sentence.encode())
modifiedSentence = clientSocket.recv(1024)
print(’From Server: ’, modifiedSentence.decode())
clientSocket.close()


TCP server
from socket import *
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((’’, serverPort))
serverSocket.listen(1)
print(’The server is ready to receive’)
while True:
	connectionSocket, addr = serverSocket.accept()
	sentence = connectionSocket.recv(1024).decode()
	capitalizedSentence = sentence.upper()
	connectionSocket.send(capitalizedSentence.encode())
	connectionSocket.close()

'''

'''
UDP CLIENT
from socket import *
serverName = ’hostname’
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
message = raw_input(’Input lowercase sentence:’)
clientSocket.sendto(message.encode(),(serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print(modifiedMessage.decode())
clientSocket.close()


UDP SERVER
from socket import *
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((’’, serverPort))
print(”The server is ready to receive”)
while True:
	message, clientAddress = serverSocket.recvfrom(2048)
	modifiedMessage = message.decode().upper()
	serverSocket.sendto(modifiedMessage.encode(), clientAddress)

'''



'''
   1 import socket
   2 
   3 UDP_IP = "127.0.0.1"
   4 UDP_PORT = 5005
   5 MESSAGE = b"Hello, World!"
   6 
   7 print("UDP target IP: %s" % UDP_IP)
   8 print("UDP target port: %s" % UDP_PORT)
   9 print("message: %s" % MESSAGE)
  10 
  11 sock = socket.socket(socket.AF_INET, # Internet
  12                      socket.SOCK_DGRAM) # UDP

  11     
  SocketRDP.PUERTO = nuevo
  13 sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

'''''''''