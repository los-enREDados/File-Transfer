import os
from lib.SocketRDT import SocketRDT
from lib.constants import ClientFlags
import lib.ProtocoloFS
from sys import argv
from lib.SocketRDT import ConnectionTimedOutError
import lib.constants
from sys import argv
import time


class uploader_flags:
    verbosity: bool
    host: str
    port: int
    myIp: str
    src: str
    name: str

    def __init__(self):
        self.verbosity = lib.constants.DEFAULT_CLIENT_VERBOSITY
        self.host = lib.constants.DEFAULT_SERVER_IP
        self.port = lib.constants.DEFAULT_SERVER_PORT
        self.myIp = lib.constants.DEFAULT_CLIENT_IP
        self.src = ""
        self.name = ""

        

def upload(flags):
    print(f"Soy {flags.myIp}")
    print(f"Quiero conectarme con : {flags.host}:{flags.port}")
    
    peerAddres = (flags.host, flags.port)
    
    ownIp = lib.constants.DEFAULT_CLIENT_IP if flags.myIp is None  else flags.myIp
    # Esto es para que si la ip no se puede asignar, se reintente con localhost
    try:
        serverSCK = SocketRDT(lib.constants.TIPODEPROTOCOLO, lib.constants.UPLOAD, peerAddres, ownIp)
    except OSError as e:
        print(f"Error al crear el socket. Reasignando Ip al cliente: {lib.constants.DEFAULT_CLIENT_IP}")
        serverSCK = SocketRDT(lib.constants.TIPODEPROTOCOLO, lib.constants.UPLOAD, peerAddres, lib.constants.DEFAULT_CLIENT_IP)
        
    print(f"Puerto ANTES de conectarme: {serverSCK.peerAddr[lib.constants.PUERTOTUPLA]}")


    # FALTA IMPLEMENTAR:
    #   *modos verbose y quiet
    #   *flags.name
    # Connect debería recibir los flags y laburar en base a eso
    



    try:
       serverSCK.connect(lib.constants.UPLOAD, flags.name)
    except ConnectionTimedOutError as e:
       print(e)
    
    # NOTE: Si no tiene el "/" final, se la anado
    try :
        if flags.src[-1] != "/":
            flags.src += "/"
        lib.ProtocoloFS.mandarArchivo(serverSCK, flags.src+flags.name)
    except AttributeError:
        print("Por favor ingrese el archivo a subir con -n y el path con -s")
    except ConnectionTimedOutError:
        print("Connection Timed Out ")

def main():
    flags = uploader_flags()
    i = 1
    while i < len(argv):
        if argv[i] == ClientFlags.HELP.value or argv[i] == ClientFlags.HELPL.value:
            print("usage : upload [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - s FILEPATH ] [ - n FILENAME ]\n\n" + 
                "< command description > \n\n" +
                "optional arguments : \n"
                "-h , --help       show this help message and exit \n"
                "-v , --verbose    increase output verbosity \n"
                "-q , --quiet      decrease output verbosity \n"
                "-H , --host       server IP address \n"
                "-p , --port       server port \n"
                "-m , --myIp       my IP address (default 127.0.0.2) \n"
                "-s , --src        source file path \n"
                "-n , --name       file name\n"
                )
            return
        elif argv[i] == ClientFlags.VERBOSE.value or argv[i] == ClientFlags.VERBOSEL.value:
            flags.verbosity = lib.constants.VERBOSE
            i += 1

        elif argv[i] == ClientFlags.QUIET.value or argv[i] == ClientFlags.QUIETL.value:
            flags.verbosity = lib.constants.QUIET
            i += 1

        elif argv[i] == ClientFlags.HOST.value or argv[i] == ClientFlags.HOSTL.value:
            flags.host = argv[i+1]
            i += 2

        elif argv[i] == ClientFlags.PORT.value or argv[i] == ClientFlags.PORTL.value:
            flags.port = int(argv[i+1])
            i += 2

        elif argv[i] == ClientFlags.MYIP.value or argv[i] == ClientFlags.MYIPL.value:
            flags.myIp = argv[i+1]
            i += 2

        elif argv[i] == ClientFlags.SRC.value or argv[i] == ClientFlags.SRCL.value:
            flags.src = argv[i+1]
            i += 2

        elif argv[i] == ClientFlags.NAME.value or argv[i] == ClientFlags.NAMEL.value:
            flags.name = argv[i+1]
            i += 2

        else:
            print(f"Flag {argv[i]} no reconocida")
            return

    print(f"flags.src = {flags.src}")
    print(f"flags.name = {flags.name}")
    if os.path.isdir(flags.src) == False:
        print(f"El directorio {(flags.src)} no existe")
        return

    if os.path.isfile(flags.src+flags.name) == False:
        print(f"El archivo {flags.src+flags.name} no existe")
        return

    if os.path.getsize(flags.src+flags.name) >= lib.constants.MAXFILESIZE:
        print(f"El archivo {flags.src+flags.name} es demasiado grande")
        return

            
    upload(flags)

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    elapsed_time = end_time - start_time
