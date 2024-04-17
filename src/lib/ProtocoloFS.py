from lib.SocketRDT import SocketRDT
import lib.constants

# F.S.: File Sharing
# self.socketRDT = SocketRDT(lib.constants.TIPODEPROTOCOLO,

# WARNING: Aca leo la TOTALIDAD del archivo y lo cargo en memoria de
# una simplememente para tener muchos bytes en memoria.
# TODO: Hacer que esta funcion lea de a muchos bytes. Linea por linea
# es muy pocos bytes y va a hacer que tarde una banda
# Que lea de a 1000 bytes? 1024? 3000? Quien sabe
# Sea lo que sea, que sea una constante
def mandarArchivo(socketCliente: SocketRDT, archivoNombre: str):
    with open(archivoNombre, "r") as file:
        archivo = file.read()
        # print(archivo)
        # print(len(archivo))
        # print(len(archivo.encode('utf-8')))
        # print(len(archivo))

        archivoEnBytes = archivo.encode('utf-8')
        socketCliente.sendall(archivoEnBytes)

        # for line in f:
        #     print(line)
        #     print(len(line.encode('utf-8')))
        #     break

    return
