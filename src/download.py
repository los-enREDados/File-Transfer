from lib.SocketRDT import SocketRDT

import lib.ProtocoloFS
from sys import argv
from lib.constants import Mode, ClientFlags
import lib.constants
UDP_IP = "10.0.0.4"
UDP_PORT = 5005
MESSAGE = b"Hello, World!"

class downloader_flags:
    mode: lib.constants.Mode
    host: str
    port: str
    dst: str
    name: str

def download(flags: downloader_flags):
    print("UDP target IP: %s" % flags.host)
    print("UDP target port: %s" % flags.port)


    peerAddres = (flags.host, flags.port)

    # WARNING: Aca digo que "myIP" es localhost. No estoy 100% de que
    # eso aplique para todos los casos. Esto me hace pensar que ni
    # hace falta almacenar "myAddress". Para pensar
    serverSCK = SocketRDT(lib.constants.TIPODEPROTOCOLO, lib.constants.DOWNLOAD, peerAddres, "10.0.0.4")


    print("mi puerto es ", serverSCK.myAddress[1])
    print(f"Puerto ANTES de conectarme: {serverSCK.peerAddr[lib.constants.PUERTOTUPLA]}")

    serverSCK.connect(lib.constants.DOWNLOAD, flags.name)
   

    archivo = lib.ProtocoloFS.recibirArchivo(serverSCK, flags.name)
    
    print("\033[92mArchivo Recibido!\033[0m")

    with open(flags.dst + flags.name, "wb") as file:
        file.write(archivo)


def main():
    # TODO: Hacer que ande con las flags
    # por ahora lo hacemos asi para que ande
    flags = downloader_flags()
    flags.mode = Mode.NORMAL
    i = 1
    while i < len(argv):
        if argv[i] == ClientFlags.HELP.value:
            print(
                "usage : download [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - d FILEPATH ] [ - n FILENAME ]\n\n"
                "< command description >\n\n"
                "optional arguments :\n"
                "-h , -- help show this help message and exit\n"
                "-v , -- verbose increase output verbosity\n"
                "-q , -- quiet decrease output verbosity\n"
                "-H , -- host server IP address\n"
                "-p , -- port server port\n"
                "-d , -- dst destination file path\n"
                "-n , -- name file name\n"
                )
            return
        elif argv[i] == ClientFlags.VERBOSE.value:
            flags.mode = Mode.VERBOSE
            i += 1

        elif argv[i] == ClientFlags.QUIET.value:
            flags.mode = Mode.QUIET
            i += 1

        elif argv[i] == ClientFlags.HOST.value:
            flags.host = argv[i+1]
            i += 2

        elif argv[i] == ClientFlags.PORT.value:
            flags.port = int(argv[i+1])
            i += 2

        elif argv[i] == ClientFlags.DST.value:
            flags.dst = argv[i+1]
            i += 2

        elif argv[i] == ClientFlags.NAME.value:
            flags.name = argv[i+1]
            i += 2
    download(flags)
main()

