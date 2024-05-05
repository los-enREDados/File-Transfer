from lib.SocketRDT import SocketRDT, strABytes
import lib.constants


# F.S.: File Sharing
# self.socketRDT = SocketRDT(lib.constants.TIPODEPROTOCOLO,

# WARNING: Aca leo la TOTALIDAD del archivo y lo cargo en memoria de
# una simplememente para tener muchos bytes en memoria.
# TODO: Hacer que esta funcion lea de a muchos bytes. Linea por linea
# es muy pocos bytes y va a hacer que tarde una banda
# Que lea de a 1000 bytes? 1024? 3000? Quien sabe
# Sea lo que sea, que sea una constante
def mandarArchivo(serverSCK: SocketRDT, archivoNombre: str):
    # Protocolo de subida de archivos:
    # 1. Cliente envia "upload"
    # 3. Cliente envia el archivo
    # 4. Servidor responde con la cantidad de bytes leidos


    # nombreArchivo = strABytes(archivoNombre)
    # mensaje = lib.constants.MENSAJEUPLOAD + nombreArchivo

    
    # serverSCK.sendall(mensaje)
  
    # ack = serverSCK.receive_all()
    # if ack != "ack":
    #     print("Error en la conexión")
    #     return
    
    with open(archivoNombre, "rb") as file:
        archivo = file.read()
        serverSCK.sendall(archivo)

    # bytes_read = serverSCK.receive_all()
    # if bytes_read != len(archivo):
    #     print("Error al subir el archivo")

    return 

def recibirArchivo(serverSCK: SocketRDT, pathDelArchivoADescargar: str):
    downloaded_file = serverSCK.receive_all()
   
    return downloaded_file
