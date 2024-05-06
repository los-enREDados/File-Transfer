import sys
import socket
# import struct
import os

import lib.SocketRDT 

class server_state_flags:
    verbosity: lib.constants.Verbosity
    host: str
    port: int
    stge: str
    name: str
    verbose: bool

    def __init__(self):
        self.verbosity = lib.constants.DEFAULT_SERVER_VERBOSITY
        self.host = lib.constants.DEFAULT_SERVER_IP
        self.port = lib.constants.DEFAULT_SERVER_PORT
        self.stge = lib.constants.DEFAULT_SERVER_STORAGE
        

#    DIR.archivo
from lib.SocketRDT import SocketRDT, bytesAstr, uint32Aint , ConnectionTimedOutError, ConnectionAttemptTimedOutError
import lib.ProtocoloFS
import lib.constants
from lib.constants import IP, PORT
from lib.constants import ServerFlags, Verbosity
import threading
from sys import argv


# SERVER_PATH = "../data/server/"

class State:
    def __init__(self):
        self.estado = True

class Server:
        def __init__ (self, flags):
            self.flags = flags

            ip = flags.host
            port = flags.port
            

            self.recieveSocket = SocketRDT(lib.constants.TIPODEPROTOCOLO, None,
                                        (0,0), ip, port)
            self.conexiones = {}
            self.seguir_corriendo = State()
            self.listener = None

            self.proximoPuerto = port + 1

        def start(self):
            self.listener = threading.Thread(target=self.listen, args=(self.seguir_corriendo,))
            print("\033[94m+------------------------------------------------+")
            print(f"| Hola soy el Servidor y estoy en \033[93m{self.recieveSocket.myAddress[0]}:{self.recieveSocket.myAddress[1]}\033[94m |")
            print("+------------------------------------------------+\033[0m")
            
            self.listener.start()
            while self.seguir_corriendo.estado:
                input_server = input("      Presione q para cerrar el servidor\n")
                if input_server == "q":
                    self.seguir_corriendo.estado = False
                    print("Cerrando servidor...")

            self.shutdown()

        def shutdown(self):
            self.seguir_corriendo.estado = False
            print(f'mato listener')
            self.listener.join()
            self.recieveSocket.shutdown()
            print(f'mato conexiones')
            for conexion in self.conexiones.values():
                print(f"Apagando conexion {conexion.id}")
                self.conexiones[conexion.id].estado.estado = False
                conexion.socketRDT.shutdown()
                conexion.join()
            
        def check_dead(self):
            deads = []
            for conexion in self.conexiones.values():
                print(f"Chequeando conexion {conexion.id}")
                if not conexion.estado.estado:
                    print(f"Conexion {conexion.id} ha muerto")
                    deads.append(conexion.id)

            for id in deads:
                self.conexiones.pop(id)

        def listen(self, seguir_corriendo):
            while seguir_corriendo.estado:
                print("Escuchando conexiones...")
                try: 
                    paquete, addr  = self.recieveSocket.acceptConnection() # Añadir modo (verbose, quiet)
                    if (not paquete or addr[1] in self.conexiones):
                        continue

                    print(f"Recibi un paquete de {addr}")
                    print(f"Hago el handshake con {addr}")
                    self.handshake(addr, paquete) # Añadir modo (verbose, quiet)
                    print(f"Termine el handshake con {addr}")
  
                except ConnectionAttemptTimedOutError:
                    pass

                self.check_dead()

        def handshake(self, addressCliente, paquete):
            myIp = self.recieveSocket.myAddress[IP]

            try :
                socketRDT = SocketRDT(lib.constants.TIPODEPROTOCOLO, paquete.tipo, addressCliente, myIp, self.proximoPuerto)
            except socket.error as e:
                print(f"Error al crear socket: {e}")
                self.proximoPuerto += 1
                return

            self.proximoPuerto += 1
            nuevoPuerto = socketRDT.skt.getsockname()[1]
            # try :
            self.recieveSocket.syncAck(nuevoPuerto, socketRDT, paquete) # Añadir modo (verbose, quiet)
            # except ConnectionTimedOutError:
            #     pass #Solo ignoro el error ya que se asume conexion

            # NOTE: Aca arranca el nuevo thread
            print(f"[Nuevo cliente: {addressCliente}]")
            w = worker(socketRDT, paquete, self.flags.stge) # self.flags.stge) # Añadir modo (verbose, quiet)
            w.run()
            self.conexiones[socketRDT.peerAddr[1]] = w


class worker: 
    def __init__(self, socketRDT, paquete, storage): 
        self.socketRDT = socketRDT
        self.paquete = paquete
        self.addressCliente = socketRDT.peerAddr
        self.nombre = bytesAstr(paquete.getPayload())
        self.tipo = paquete.tipo
        self.id = socketRDT.peerAddr[1]
        self.estado = State()
        self.storage = storage
        self.thread = threading.Thread(target=work, args=(self.socketRDT, self.paquete, self.estado, self.storage))

    def run(self):
        try :
            self.thread.start()
        except Exception as e:
            print(f"Error en worker {self.id}: {e}")
            self.estado = False

    def join(self):
        self.thread.join()

def work(socketRDT, paquete, state, stge):
    addressCliente = socketRDT.peerAddr
    nombre = bytesAstr(paquete.getPayload())
    print(nombre)
    tipo = paquete.tipo

    if tipo == lib.constants.UPLOAD:

        nombreArchivo = nombre.split("/")[-1]
        print(f"Me esta llegando el archivo: {nombreArchivo}")
    
        try:
            archivo_recibido = socketRDT.receive_all()
        except ConnectionTimedOutError as e:
            print(f"Murio la conexion con {addressCliente}")
            state.estado = False
            return
            
    
        print("\033[92mArchivo Recibido!\033[0m")

        print(stge)
        print(nombreArchivo)
        with open(stge + nombreArchivo, "wb") as file:
            file.write(archivo_recibido) # Añadir modo (verbose, quiet)

        print(f'Cambiando estado de {addressCliente} a False')
        state.estado = False


    elif tipo == lib.constants.DOWNLOAD:
        stge = "data/server/"
      
        try: 
            print(f"\033[93mEnviando {stge} + {nombre} a {addressCliente}...\033[0m")
            
            with open(stge + nombre, "rb") as file:
                archivo = file.read()    
                try: 
                    socketRDT.sendall(archivo)
                except Exception as e:
                    print(f"Murio la conexion con {addressCliente}")
                    state.estado = False
                    return
            print(f"\033[92mArchivo {nombre} enviado a {addressCliente}!\033[0m")

        except FileNotFoundError:
            print(f"El archivo {nombre} no existe")
            
    state.estado = False


def __main__():
    flags = server_state_flags()
    i = 1
    while i < len(argv):
        if argv[i] == ServerFlags.HELP.value or argv[i] == ServerFlags.HELPL.value:
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
            flags.mode = Verbosity.VERBOSE
            i += 1

        elif argv[i] == ServerFlags.QUIET.value:
            flags.mode = Verbosity.QUIET
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
    # o sacar ip y puerto de aca, o hacer que server reciba flags
    server = Server(flags)
    server.start()

__main__()
