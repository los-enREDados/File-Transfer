from lib.SocketRDT import SocketRDT


def mandarArchivo(serverSCK: SocketRDT, archivoNombre: str, archivoPath):

    with open(archivoPath + archivoNombre, "rb") as file:
        archivo = file.read()
        serverSCK.sendall(archivo)

    return


def recibirArchivo(serverSCK: SocketRDT):

    downloaded_file = serverSCK.receive_all()
    return downloaded_file
