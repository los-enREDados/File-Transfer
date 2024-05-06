import sys
import socket
# import struct
import os

import lib.SocketRDT 
print(os.getcwd())


#    DIR.archivo
from lib.SocketRDT import SocketRDT, bytesAstr, uint32Aint , ConnectionTimedOutError, ConnectionAttemptTimedOutError
import lib.ProtocoloFS
import lib.constants
import threading


UDP_IP = "127.0.0.1"
UDP_PORT = 5005

SERVER_PATH = "data/server/"



class State:
    def __init__(self):
        self.estado = True


class Server:
        def __init__ (self, ip, port):
            self.recieveSocket = SocketRDT(lib.constants.TIPODEPROTOCOLO, None,
                                        (0,0), ip, port)
            self.conexiones = {}
            self.seguir_corriendo = State()
            self.listener = None

        def start(self):
            self.listener = threading.Thread(target=self.listen, args=(self.seguir_corriendo,))

            print(f"Hola soy el Servidor y estoy en {UDP_IP}:{UDP_PORT}")
            self.listener.start()
            while self.seguir_corriendo.estado:
                input_server = input("Presione q para cerrar el servidor \n")
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
            print("Chequeando conexiones...")
            for conexion in self.conexiones.values():
                print(f"Chequeando conexion {conexion.id}")
                if not conexion.estado.estado:
                    print(f"Conexion {conexion.id} ha muerto")
                    deads.append(conexion.id)

            for id in deads:
                self.conexiones.pop(id)


        def listen(self, seguir_corriendo):
            print("Escuchando conexiones...")
            while seguir_corriendo.estado:
                try: 
                    paquete, addr  = self.recieveSocket.acceptConnection()
                    if (not paquete or addr[1] in self.conexiones):
                        continue

                    print(f"Recibi un paquete de {addr}")
                    print(f"Hago el handshake con {addr}")
                    self.handshake(addr, UDP_IP, paquete)
                    print(f"Termine el handshake con {addr}")
  
                except ConnectionAttemptTimedOutError as e:
                    pass

                self.check_dead()

            

        def handshake(self, addressCliente, myIP, paquete):
            socketRDT = SocketRDT(lib.constants.TIPODEPROTOCOLO, paquete.tipo, addressCliente, myIP)
            nuevoPuerto = socketRDT.skt.getsockname()[1]
            try :
                self.recieveSocket.syncAck(nuevoPuerto, socketRDT, paquete)
            except ConnectionTimedOutError:
                pass #Solo ignoro el error ya que se asume conexion

            print(f"[Nuevo cliente: {addressCliente}]")
            w = worker(socketRDT, paquete)
            w.run()
            self.conexiones[socketRDT.peerAddr[1]] = w

class worker: 
    def __init__(self, socketRDT, paquete):
        self.socketRDT = socketRDT
        self.paquete = paquete
        self.addressCliente = socketRDT.peerAddr
        self.nombre = bytesAstr(paquete.getPayload())
        self.tipo = paquete.tipo
        self.id = socketRDT.peerAddr[1]
        self.estado = State()
        self.thread = threading.Thread(target=work, args=(self.socketRDT, self.paquete, self.estado))

    def run(self):
        try :
            self.thread.start()
        except Exception as e:
            print(f"Error en worker {self.id}: {e}")
            self.estado = False

    def join(self):
        self.thread.join()

def work(socketRDT, paquete, state):
    addressCliente = socketRDT.peerAddr
    nombre = bytesAstr(paquete.getPayload())
    tipo = paquete.tipo

    if tipo == lib.constants.UPLOAD:

        nombreArchivo = nombre.split("/")[-1]
    
        # TODO: No me capta el tipo correctamente. Arreglar
        # if tipo == lib.constants.MENSAJEUPLOAD:
        #archivo_recibido = lib.ProtocoloFS.recibirArchivo(socketRDT, pathArchivo)
        
        try:
            archivo_recibido = socketRDT.receive_all()
        except Exception as e:
            print(f"Murio la conexion con {addressCliente}")
            state.estado = False
            return
            
    
        print("\033[92mArchivo Recibido!\033[0m")


        with open(SERVER_PATH + nombreArchivo, "wb") as file:
            file.write(archivo_recibido)

        print(f'Cambiando estado de {addressCliente} a False')
        state.estado = False


    elif tipo == lib.constants.DOWNLOAD:

        try: 
            print(f"\033[93mEnviando '{nombre}' a {addressCliente}...\033[0m")
            
            with open(nombre, "rb") as file:
                archivo = file.read()
            
                try: 
                    socketRDT.sendall(archivo)
                except Exception as e:
                    print(f"Murio la conexion con {addressCliente}")
                    state.estado = False
                    return
                
        except FileNotFoundError:
            print(f"El archivo {nombre} no existe")
            
    state.estado = False

    


def __main__():
    if lib.constants.TIPODEPROTOCOLO != "SW" and lib.constants.TIPODEPROTOCOLO != "SR":
        sys.exit(f'''
\033[91mERROR\033[0m: Tipo de protocolo desconocido: {lib.constants.TIPODEPROTOCOLO}''')

    server = Server(UDP_IP, UDP_PORT)
    server.start()

__main__()
