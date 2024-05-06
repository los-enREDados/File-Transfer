from lib.SocketRDT import SocketRDT
from lib.constants import ClientFlags, Mode
import lib.ProtocoloFS
from sys import argv
from lib.constants import constants

class uploader_flags:
    mode: Mode
    host: str
    port: str
    myIp: str
    src: str
    name: str

    def __init__(self):
        self.mode = Mode.NORMAL
        self.host = constants.DEFAULT_SERVER_IP
        self.port = constants.DEFAULT_SERVER_PORT
        self.myIp = constants.DEFAULT_CLIENT_IP
        

def upload(flags):
    print(f"Soy {flags.myIp}")
    print(f"Quiero conectarme con : {flags.host}:{flags.port}")
    
    peerAddres = (flags.host, flags.port)

    ownIp = constants.DEFAULT_CLIENT_IP if flags.myIp is None  else flags.myIp
    try:
        serverSCK = SocketRDT(lib.constants.TIPODEPROTOCOLO, lib.constants.UPLOAD, peerAddres, ownIp)
    except OSError as e:
        print(f"Error al crear el socket. Reasignando Ip al cliente: {constants.DEFAULT_CLIENT_IP}")
        serverSCK = SocketRDT(lib.constants.TIPODEPROTOCOLO, lib.constants.UPLOAD, peerAddres, constants.DEFAULT_CLIENT_IP)
        
    print(f"Puerto ANTES de conectarme: {serverSCK.peerAddr[lib.constants.PUERTOTUPLA]}")

    # FALTA IMPLEMENTAR:
    #   *modos verbose y quiet
    #   *flags.name
    # Connect debería recibir los flags y laburar en base a eso
    serverSCK.connect(lib.constants.UPLOAD, flags.name)

    lib.ProtocoloFS.mandarArchivo(serverSCK, flags.src+"/"+flags.name)


def main():

    flags = uploader_flags()
    flags.mode = Mode.NORMAL
    i = 1

    while i < len(argv):
        if argv[i] == ClientFlags.HELP.value:
            print("usage : upload [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - s FILEPATH ] [ - n FILENAME ]\n\n" + 
                "< command description > \n\n" +
                "optional arguments : \n"
                "-h , -- help show this help message and exit \n"
                "-v , -- verbose increase output verbosity \n"
                "-q , -- quiet decrease output verbosity \n"
                "-H , -- host server IP address \n"
                "-p , -- port server port \n"
                "-m , -- myIp my IP address (default 127.0.0.2) \n"
                "-s , -- src source file path \n"
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

        elif argv[i] == ClientFlags.MYIP.value:
            flags.myIp = argv[i+1]
            i += 2

        elif argv[i] == ClientFlags.SRC.value:
            flags.src = argv[i+1]
            i += 2

        elif argv[i] == ClientFlags.NAME.value:
            flags.name = argv[i+1]
            i += 2

    upload(flags)

if __name__ == "__main__":
    main()
