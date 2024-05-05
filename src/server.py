import sys
import socket
# import struct
import os

import lib.SocketRDT 
print(os.getcwd())

class server_state_flags:
    mode: lib.constants.Mode
    host: str
    port: int
    stge: str
    name: str

#    DIR.archivo
from lib.SocketRDT import SocketRDT, bytesAstr, uint32Aint
import lib.ProtocoloFS
import lib.constants
from lib.constants import ServerFlags, Mode
import threading
from sys import argv


UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# SERVER_PATH = "../data/server/"



seguir_corriendo = True
lock = threading.Lock()


def input_server():
    global seguir_corriendo
    res = input("Presione q para cerrar el servidor")
    if res == "q":
        with lock:
            seguir_corriendo = False

        print("Cerrando servidor...")

class Listener:
        recieveSocket : SocketRDT
        flags : server_state_flags

        def __init__ (self, flags):
            self.flags = flags
            self.recieveSocket = SocketRDT(lib.constants.TIPODEPROTOCOLO, None,
                                        (0,0), flags.host, flags.port)

        def listen(self):
            # TODO: Poner en un loop y hacer que esto sea multithread
            # Cada worker deberia estar en su propio thread
            paquete, addr  = self.recieveSocket.acceptConnection() # Añadir modo (verbose, quiet)

            self.handshake(addr, paquete) # Añadir modo (verbose, quiet)

            # self.handshake(addr, UDP_IP, paquete)
            # worker(addr, UDP_IP)
            # w = Worker(addr, UDP_IP)
            # w.hablar()

        def handshake(self, addressCliente, paquete):
            socketRDT = SocketRDT(lib.constants.TIPODEPROTOCOLO, paquete.tipo, addressCliente, self.flags.host)
            nuevoPuerto = socketRDT.skt.getsockname()[1] 
            self.recieveSocket.syncAck(nuevoPuerto, socketRDT, paquete) # Añadir modo (verbose, quiet)

            worker(socketRDT, paquete, self.flags.stge) # Añadir modo (verbose, quiet)


def worker(socketRDT, paquete, stge, mode = Mode.NORMAL):
    # socketRDT = SocketRDT(lib.constants.TIPODEPROTOCOLO, addressCliente, myIP)
    # socketRDT.syncAck()
    # addressCliente = socketRDT.skt.getpeername() 
    addressCliente = socketRDT.peerAddr
    nombre = bytesAstr(paquete.getPayload())
    tipo = paquete.tipo
    # Con esto vemos si es upload (UPL) o Download (DOW)
    # Por ahora que solo estamos implementando upload no lo usamos
    
    # pathArchivo = nombre[len(lib.constants.MENSAJEUPLOAD):]
    # pathArchivo = bytesAstr(pathArchivo)

    if tipo == lib.constants.UPLOAD:

        nombreArchivo = nombre.split("/")[-1]
    
        # TODO: No me capta el tipo correctamente. Arreglar
        # if tipo == lib.constants.MENSAJEUPLOAD:
        #archivo_recibido = lib.ProtocoloFS.recibirArchivo(socketRDT, pathArchivo)
        
        # print(f"\033[93mRecibiendo '{nombreArchivo}' de {addressCliente}...\033[0m")
        archivo_recibido = socketRDT.receive_all() # Añadir modo (verbose, quiet)
    
        print("\033[92mArchivo Recibido!\033[0m")


        with open(stge + nombreArchivo, "wb") as file:
            file.write(archivo_recibido) # Añadir modo (verbose, quiet)


    elif tipo == lib.constants.DOWNLOAD:
        socketRDT.sendall("ack".encode()) # Añadir modo (verbose, quiet)

        try: 
            print(f"\033[93mEnviando '{stge + nombre}' a {addressCliente}...\033[0m")
            
            with open(stge + nombre, "rb") as file:
                archivo = file.read()
            
                socketRDT.sendall(archivo) # Añadir modo (verbose, quiet)
                
        except FileNotFoundError:
            print(f"El archivo {nombre} no existe")
            


    

# class Worker:
#     def __init__ (self, addressCliente, myIP):
#         self.socketRDT = SocketRDT(lib.constants.TIPODEPROTOCOLO, addressCliente, myIP)

#         self.socketRDT.syncAck()

#         self.socketRDT.receive_all(mensaje)

#         if mensaje == "voy a subir":
#             upload()
#         else:
#             download()


#         print(f"Creo un worker con Puerto: {self.socketRDT.peerAddr[lib.constants.PUERTOTUPLA]}")
        
#     def hablar(self):
#         data = self.socketRDT.receive_all()
#         print ("\033[94mEl worker recibió: ", data.decode('utf-8'), " de: ", self.socketRDT.peerAddr[lib.constants.PUERTOTUPLA], "\n \033[0")

#         message = data.upper()
#         message_bytes = bytes(f"{message}", 'utf-8')

#         self.socketRDT.sendall(message_bytes)
    
    


def __main__():

    flags = server_state_flags()
    i = 1
    while i < len(argv):
        if argv[i] == ServerFlags.HELP.value:
            print(
                "usage : start - server [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - s DIRPATH ]\n\n"
                "< command description >\n\n"
                "optional arguments :\n"
                "-h , -- help show this help message and exit\n"
                "-v , -- verbose increase output verbosity\n"
                "-q , -- quiet decrease output verbosity\n"
                "-H , -- host service IP address\n"
                "-p , -- port service port\n"
                "-s , -- storage storage dir path\n"
                )
            return
        elif argv[i] == ServerFlags.VERBOSE.value:
            flags.mode = Mode.VERBOSE
            i += 1

        elif argv[i] == ServerFlags.QUIET.value:
            flags.mode = Mode.QUIET
            i += 1

        elif argv[i] == ServerFlags.HOST.value:
            flags.host = argv[i+1]
            i += 2

        elif argv[i] == ServerFlags.PORT.value:
            flags.port = int(argv[i+1])
            i += 2

        elif argv[i] == ServerFlags.STORAGE.value:
            flags.stge = argv[i+1]
            i += 2

    if lib.constants.TIPODEPROTOCOLO != "SW" and lib.constants.TIPODEPROTOCOLO != "SR":
        sys.exit(f'''
\033[91mERROR\033[0m: Tipo de protocolo desconocido: {lib.constants.TIPODEPROTOCOLO}''')

    l = Listener(flags)
    l.listen()

__main__()
