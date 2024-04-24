from lib.SocketRDT import SocketRDT, Tipo
import lib.constants
import lib.ProtocoloFS
from sys import argv

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = b"Hello, World!"



def upload(path):
    print("UDP target IP: %s" % UDP_IP)
    print("UDP target port: %s" % UDP_PORT)


    peerAddres = (UDP_IP, UDP_PORT)

    # WARNING: Aca digo que "myIP" es localhost. No estoy 100% de que
    # eso aplique para todos los casos. Esto me hace pensar que ni
    # hace falta almacenar "myAddress". Para pensar
    serverSCK = SocketRDT(lib.constants.TIPODEPROTOCOLO, peerAddres, "127.0.0.2")

    print(f"Puerto ANTES de conectarme: {serverSCK.peerAddr[lib.constants.PUERTOTUPLA]}")

    serverSCK.connect()

    
    lib.ProtocoloFS.mandarArchivo(serverSCK, path)


def main():
    # TODO: Hacer que ande con las flags
    # por ahora lo hacemos asi para que ande
    upload(argv[1])
main()
