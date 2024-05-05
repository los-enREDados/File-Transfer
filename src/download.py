from lib.SocketRDT import SocketRDT
import lib.constants
import lib.ProtocoloFS
from sys import argv

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = b"Hello, World!"


def download(path):
    print("UDP target IP: %s" % UDP_IP)
    print("UDP target port: %s" % UDP_PORT)


    peerAddres = (UDP_IP, UDP_PORT)

    # WARNING: Aca digo que "myIP" es localhost. No estoy 100% de que
    # eso aplique para todos los casos. Esto me hace pensar que ni
    # hace falta almacenar "myAddress". Para pensar
    serverSCK = SocketRDT(lib.constants.TIPODEPROTOCOLO, lib.constants.DOWNLOAD, peerAddres, "127.0.0.2")


    print("mi puerto es ", serverSCK.myAddress[1])
    print(f"Puerto ANTES de conectarme: {serverSCK.peerAddr[lib.constants.PUERTOTUPLA]}")

    res = serverSCK.connect(lib.constants.DOWNLOAD, path)
    if not res:
        print("Connection Timed out")
        return

    archivo = lib.ProtocoloFS.recibirArchivo(serverSCK, "../data/server/"+path)
    
    print("\033[92mArchivo Recibido!\033[0m")

    with open("../data/cliente/" + path, "wb") as file:
        file.write(archivo)


def main():
    # TODO: Hacer que ande con las flags
    # por ahora lo hacemos asi para que ande
    download(argv[1])
main()
