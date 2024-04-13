import socket

#    DIR.archivo
from lib.SocketRDT import SocketRDT
import lib.constants

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = b"Hello, World!"


def main():
    print("UDP target IP: %s" % UDP_IP)
    print("UDP target port: %s" % UDP_PORT)
    print("message: %s" % MESSAGE)

    # WARNING: Aca digo que "myIP" es localhost. No estoy 100% de que
    # eso aplique para todos los casos. Esto me hace pensar que ni
    # hace falta almacenar "myAddress". Para pensar
    peerAddres = (UDP_IP, UDP_PORT)

    server = SocketRDT("SW", peerAddres, "127.0.0.1")

    print(f"Puerto ANTES de conectarme: {server.peerAddr[lib.constants.PUERTOTUPLA]}")

    server.connect()

    print(f"Puerto DESPUES de conectarme: {server.peerAddr[lib.constants.PUERTOTUPLA]}")

    print("Envio data al servidor")
    server.sendall(MESSAGE)

    print("Espero data del worker")
    data = server.receive_all()

    print("Recibí del worker: ", data)

main()

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
