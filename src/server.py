import sys
import socket
# import struct
import os 
print(os.getcwd())


#    DIR.archivo
from lib.SocketRDT import SocketRDT, bytesAstr, uint32Aint
import lib.ProtocoloFS
import lib.constants
import threading


UDP_IP = "127.0.0.1"
UDP_PORT = 5005

SERVER_PATH = "../data/server/"



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
    
    def __init__ (self, ip, port):
        self.recieveSocket = SocketRDT(lib.constants.TIPODEPROTOCOLO,
                                       (0,0), ip, port)

    def listen(self):
        # TODO: Poner en un loop y hacer que esto sea multithread
        # Cada worker deberia estar en su propio thread
        ts = []

        global seguir_corriendo

        thread_lector_input = threading.Thread(target=input_server, args=())
        thread_lector_input.start()
     

        while True:
                
            with lock:
                if not seguir_corriendo:
                    break
            

            addr  = self.recieveSocket.acceptConnection()

            x = threading.Thread(target=worker, args=(addr, UDP_IP))
            
            ts.append(x)
            x.start()
            
            #worker(addr, UDP_IP)
        print("Saliendo del loop")
        for x in ts:
            x.join()

        # w = Worker(addr, UDP_IP)
        # w.hablar()


def worker(addressCliente, myIP):
    socketRDT = SocketRDT(lib.constants.TIPODEPROTOCOLO, addressCliente, myIP)
    socketRDT.syncAck()

    tipoYnombre = socketRDT.receive_all()
    tipo = tipoYnombre[0:len(lib.constants.MENSAJEUPLOAD)]
    # Con esto vemos si es upload (UPL) o Download (DOW)
    # Por ahora que solo estamos implementando upload no lo usamos
    
    pathArchivo = tipoYnombre[len(lib.constants.MENSAJEUPLOAD):]
    pathArchivo = bytesAstr(pathArchivo)

    if tipo == lib.constants.MENSAJEUPLOAD:

        nombreArchivo = pathArchivo.split("/")[-1]
    
        # TODO: No me capta el tipo correctamente. Arreglar
        # if tipo == lib.constants.MENSAJEUPLOAD:
        #archivo_recibido = lib.ProtocoloFS.recibirArchivo(socketRDT, pathArchivo)
        
        print(f"\033[93mRecibiendo '{nombreArchivo}' de {addressCliente}...\033[0m")
        archivo_recibido = socketRDT.receive_all()
    
        print("\033[92mArchivo Recibido!\033[0m")


        with open(SERVER_PATH + nombreArchivo, "wb") as file:
            file.write(archivo_recibido)


    elif tipo == lib.constants.MENSAJEDOWNLOAD:
        socketRDT.sendall("ack".encode())

        try: 
            print(f"\033[93mEnviando '{pathArchivo}' a {addressCliente}...\033[0m")
            
            with open(pathArchivo, "rb") as file:
                archivo = file.read()
            
                socketRDT.sendall(archivo)
                
        except FileNotFoundError:
            print(f"El archivo {pathArchivo} no existe")
            


    

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
    if lib.constants.TIPODEPROTOCOLO != "SW" and lib.constants.TIPODEPROTOCOLO != "SR":
        sys.exit(f'''
\033[91mERROR\033[0m: Tipo de protocolo desconocido: {lib.constants.TIPODEPROTOCOLO}''')

    l = Listener(UDP_IP, UDP_PORT)
    l.listen()

__main__()
