from lib.SocketRDT import SocketRDT
from lib.SocketRDT import ConnectionTimedOutError

import lib.constants
import lib.ProtocoloFS
from sys import argv

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = b"Hello, World!"


def download(path):
    print(path)

    peerAddres = (UDP_IP, UDP_PORT)


    # WARNING: Aca digo que "myIP" es localhost. No estoy 100% de que
    # eso aplique para todos los casos. Esto me hace pensar que ni
    # hace falta almacenar "myAddress". Para pensar
    serverSCK = SocketRDT(lib.constants.TIPODEPROTOCOLO, lib.constants.DOWNLOAD, peerAddres, "127.0.0.2")


    print("mi puerto es ", serverSCK.myAddress[1])
    print(f"Puerto ANTES de conectarme: {serverSCK.peerAddr[lib.constants.PUERTOTUPLA]}")

    try :
        serverSCK.connect(lib.constants.DOWNLOAD, path)
    except ConnectionTimedOutError as e:
        print(e)
        return

    archivo = lib.ProtocoloFS.recibirArchivo(serverSCK, path)
    
    nombre = path.split("/")[-1]

    with open("data/cliente/" + nombre, "wb") as file:
        file.write(archivo)


def main():
    # TODO: Hacer que ande con las flags
    # por ahora lo hacemos asi para que ande
    download(argv[1])
main()
