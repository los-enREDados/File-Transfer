from lib.SocketRDT import SocketRDT
from lib.SocketRDT import ConnectionTimedOutError, PackageError
import lib.ProtocoloFS
from sys import argv
from lib.constants import ClientFlags, pretty_print
import lib.constants
import os
import time


class downloader_flags:
    verbosity: bool
    host: str
    port: int
    myIp: str
    dst: str
    name: str

    def __init__(self):
        self.verbosity = lib.constants.DEFAULT_CLIENT_VERBOSITY
        self.host = lib.constants.DEFAULT_SERVER_IP
        self.port = lib.constants.DEFAULT_SERVER_PORT
        self.myIp = lib.constants.DEFAULT_CLIENT_IP
        self.dst = "data/cliente/"
        self.name = None


def download(flags: downloader_flags):
    start = time.time()

    peerAddres = (flags.host, flags.port)
    try:
        serverSCK = SocketRDT(
            lib.constants.TIPODEPROTOCOLO,
            lib.constants. DOWNLOAD,
            peerAddres,
            flags.verbosity,
            flags.myIp)
    except OSError:
        print(
            f"Error al crear el socket. Reasignando Ip al cliente: {lib.constants.DEFAULT_CLIENT_IP}")
        serverSCK = SocketRDT(
            lib.constants.TIPODEPROTOCOLO,
            lib.constants. DOWNLOAD,
            peerAddres,
            flags.verbosity,
            lib.constants.DEFAULT_CLIENT_IP)

    print(f"{lib.constants.BLUE}+------------------------------------------------+")
    print(
        f"| Hola soy un Cliente y estoy en {lib.constants.YELLOW}{flags.myIp}:{serverSCK.myAddress[1]}\033[94m |")
    print(f"| Quiero conectarme con : {flags.host}:{flags.port}         |")
    print("+------------------------------------------------+\033[0m")

    try:
        serverSCK.connect(lib.constants.DOWNLOAD, flags.name)
        pretty_print(
            f"\033[95mDescargando {flags.name} de {flags.myIp}:{serverSCK.myAddress[1]}",
            flags.verbosity)
        archivo = lib.ProtocoloFS.recibirArchivo(serverSCK)

    except AttributeError as e:
        print(e)
        print("Por favor ingrese nombre de archivo con las flags correspondientes\n")
        return
    except PackageError:
        print(f"\033[91m Archivo: {flags.name} no existe en el servidor")
        return
    except ConnectionTimedOutError as e:
        if flags.verbosity == lib.constants.VERBOSE:
            print()
        print(e)
        return

    print(
        f"\033[92mArchivo {flags.name} recibido! Guardando en {flags.dst + flags.name}")

    if flags.dst[-1] != "/":
        flags.dst += "/"
    with open(flags.dst + flags.name, "wb") as file:
        file.write(archivo)

    pretty_print(
        f"Tiempo de descarga: {(time.time() - start):.2f} segundos",
        flags.verbosity)


def main():
    flags = downloader_flags()
    i = 1
    while i < len(argv):
        if argv[i] == ClientFlags.HELP.value or argv[i] == ClientFlags.HELPL.value:
            print(
                "usage : download [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - d FILEPATH ] [ - n FILENAME ]\n\n"
                "< command description >\n\n"
                "optional arguments :\n"
                "-h , --help       show this help message and exit\n"
                "-v , --verbose    increase output verbosity\n"
                "-q , --quiet      decrease output verbosity\n"
                "-H , --host       server IP address\n"
                "-p , --port       server port\n"
                "-m , --myIp       my IP address (default 127.0.0.2) \n"
                "-d , --dst        destination file path\n"
                "-n , --name       file name\n")
            return
        elif argv[i] == ClientFlags.VERBOSE.value or argv[i] == ClientFlags.VERBOSEL.value:
            flags.verbosity = lib.constants.VERBOSE
            i += 1

        elif argv[i] == ClientFlags.QUIET.value or argv[i] == ClientFlags.QUIETL.value:
            flags.verbosity = lib.constants.QUIET

            i += 1

        elif argv[i] == ClientFlags.HOST.value or argv[i] == ClientFlags.HOSTL.value:
            flags.host = argv[i + 1]
            i += 2

        elif argv[i] == ClientFlags.PORT.value or argv[i] == ClientFlags.PORTL.value:
            flags.port = int(argv[i + 1])
            i += 2

        elif argv[i] == ClientFlags.MYIP.value or argv[i] == ClientFlags.MYIPL.value:
            flags.myIp = argv[i + 1]
            i += 2

        elif argv[i] == ClientFlags.DST.value or argv[i] == ClientFlags.DSTL.value:
            flags.dst = argv[i + 1]
            if os.path.isdir(flags.dst) is False:
                print(f"El directorio {flags.dst} no existe")
                return
            i += 2

        elif argv[i] == ClientFlags.NAME.value or argv[i] == ClientFlags.NAMEL.value:
            flags.name = argv[i + 1]
            i += 2

        else:
            print(f"Flag {argv[i]} no reconocida")
            return

    download(flags)


main()
