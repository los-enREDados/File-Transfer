import sys
import socket
import os

import lib.SocketRDT 
from lib.SocketRDT import SocketRDT, bytesAstr , ConnectionTimedOutError, ConnectionAttemptTimedOutError
import lib.ProtocoloFS
import lib.constants
from lib.constants import IP
from lib.constants import ServerFlags
import threading
from sys import argv



class server_state_flags:
    verbosity: bool
    host: str
    port: int
    stge: str
    name: str

    def __init__(self):
        self.verbosity = lib.constants.DEFAULT_SERVER_VERBOSITY
        self.host = lib.constants.DEFAULT_SERVER_IP
        self.port = lib.constants.DEFAULT_SERVER_PORT
        self.stge = lib.constants.DEFAULT_SERVER_STORAGE
        


class Conexion:
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
            self.seguir_corriendo = Conexion()
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
                if(self.conexiones[conexion.id].conexion.estado) :
                    print(f"Apagando conexion {conexion.id}")
                    conexion.socketRDT.shutdown()
                    self.conexiones[conexion.id].conexion.estado = False
                conexion.join()
            
        def check_dead(self):
            deads = []
            for worker in self.conexiones.values():
                if not worker.conexion.estado:
                    print(f"Conexion {worker.id} ha muerto")
                    deads.append(worker.id)

            for id in deads:
                self.conexiones.pop(id)

        def listen(self, seguir_corriendo):
            mensaje = f"Escuchando conexiones en {self.recieveSocket.myAddress[0]}:{self.recieveSocket.myAddress[1]}..."

            print(mensaje)
            while seguir_corriendo.estado:
                
                lib.constants.pretty_print(mensaje, self.flags.verbosity)                
                
                try: 
                    paquete, addr  = self.recieveSocket.acceptConnection() # Añadir modo (verbose, quiet)
                    if (not paquete or addr[1] in self.conexiones):
                        continue

                    print(f"Recibi un paquete de {addr}")
                    print(f"Hago el handshake con {addr}")
                    self.handshake(addr, paquete) # Añadir modo (verbose, quiet)
                    print(f"Termine el handshake con {addr}")
  
                except ConnectionAttemptTimedOutError or OSError:
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
            self.recieveSocket.syncAck(nuevoPuerto, socketRDT, paquete) # Añadir modo (verbose, quiet)

            # NOTE: Aca arranca el nuevo thread
            print(f"[Nuevo cliente: {addressCliente}]")
            w = worker(socketRDT, paquete, self.flags.stge) # self.flags.stge) # Añadir modo (verbose, quiet)
            w.run()
            self.conexiones[socketRDT.peerAddr[1]] = w


class worker: 
    def __init__(self, socketRDT, paquete, storage): 
        self.socketRDT = socketRDT
        self.addressCliente = socketRDT.peerAddr
        self.nombre = bytesAstr(paquete.getPayload())
        self.tipo = paquete.tipo
        self.id = socketRDT.peerAddr[1]
        self.conexion = Conexion()
        self.thread = threading.Thread(target=work, args=(self.socketRDT, paquete, self.conexion, storage))
    
    def run(self):
        try :
            self.thread.start()
        except Exception as e:
            print(f"Error en worker {self.id}: {e}")
            self.conexion.estado = False

    def join(self):
        self.thread.join()

def work(socketRDT, paquete, conexion, storage):
    addressCliente = socketRDT.peerAddr
    nombre = bytesAstr(paquete.getPayload())
    print(nombre)
    tipo = paquete.tipo
    # NOTE: Si no tiene el "/" final, se la anado
    if storage[-1] != "/":
        storage += "/"
    try :
        if tipo == lib.constants.UPLOAD:
            nombreArchivo = nombre.split("/")[-1]
            print(f"Me esta llegando el archivo: {nombreArchivo}")
        
            archivo_recibido = socketRDT.receive_all()
                
        
            print("\033[92mArchivo Recibido!\033[0m")

            print(storage)
            print(nombreArchivo)
            with open(storage + nombreArchivo, "wb") as file:
                file.write(archivo_recibido) # Añadir modo (verbose, quiet)

        elif tipo == lib.constants.DOWNLOAD:
                with open(storage + nombre, "rb") as file:
                    archivo = file.read()    
                    print(f"\033[93mEnviando {storage}/{nombre} a {addressCliente}...\033[0m")
                    socketRDT.sendall(archivo)

                print(f"\033[92mArchivo {nombre} enviado a {addressCliente}!\033[0m")

    except FileNotFoundError:
            print(f"El archivo {nombre} no existe")
            socketRDT.sendall(None)

    except ConnectionTimedOutError:
            print(f"Murio la conexion con {addressCliente}")
            conexion.estado = False
            return
        
    except OSError:
            conexion.estado = False
            return #Forced shutdown
                
    
    conexion.estado = False


def __main__():
    flags = server_state_flags()
    i = 1
    while i < len(argv):
        if argv[i] == ServerFlags.HELP.value or argv[i] == ServerFlags.HELPL.value:
            print(
                "usage : start - server [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - s DIRPATH ]\n\n"
                "< command description >\n\n"
                "optional arguments :\n"
                "-h , --help        show this help message and exit\n"
                "-v , --verbose     increase output verbosity\n"
                "-q , --quiet       decrease output verbosity\n"
                "-H , --host        service IP address\n"
                "-p , --port        service port\n"
                "-s , --storage     storage dir path\n"
                )
            return
        elif argv[i] == ServerFlags.VERBOSE.value:
            flags.verbosity = lib.constants.VERBOSE
            i += 1

        elif argv[i] == ServerFlags.QUIET.value:
            flags.verbosity = lib.constants.QUIET
            i += 1

        elif argv[i] == ServerFlags.HOST.value:
            flags.host = argv[i+1]
            i += 2

        elif argv[i] == ServerFlags.PORT.value:
            flags.port = int(argv[i+1])
            i += 2

        elif argv[i] == ServerFlags.STORAGE.value:
            flags.stge = argv[i+1]
            if os.path.isdir(flags.stge) == False:
                print(f"El directorio {flags.stge} no existe")
                return
            i += 2
    
    if lib.constants.TIPODEPROTOCOLO != "SW" and lib.constants.TIPODEPROTOCOLO != "SR":
        sys.exit(f'''
\033[91mERROR\033[0m: Tipo de protocolo desconocido: {lib.constants.TIPODEPROTOCOLO}''')
    # o sacar ip y puerto de aca, o hacer que server reciba flags
    server = Server(flags)
    server.start()

__main__()

'''
Ips y puertos default y custom Chequeadisimo
paths default y custom Chequeadisimo
verbose y quiet

opcional: que el server le avise al cliente cuando el archivo no exista, en vez de timeout
'''