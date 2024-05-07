from enum import Enum


IPTUPLA = 0
PUERTOTUPLA = 1

TIPODEPROTOCOLO = "SW" 




# Estos dos estan en bytes


# HEADER
TAMANONUMERORED = 4 #seq
TAMANOCONNECT   = 1
TAMANOTIPO      = 1
TAMANOFIN       = 1
TAMANOERROR     = 1
TAMANOHEADER    = TAMANONUMERORED + TAMANOFIN + TAMANOTIPO + TAMANOCONNECT + TAMANOERROR

#TOTAL
TAMANOPAYLOAD = 504
TAMANOPAQUETE = TAMANOPAYLOAD + TAMANOHEADER


#CONSTATS
UPLOAD = 1
DOWNLOAD = 0
CONNECT = 1
NOCONNECT = 0
FIN = 1
NOFIN = 0
ERROR = 1
NOERROR = 0
IP = 0
PORT = 1

TAMANOLECTURAARCHIVO = None

# TIMEOUTS
## CONNECT
TIMEOUTSENDER = 0.01
TIMEOUTCONNECT = 0.1
TIMEOUTACCEPT = 5
## SEND
TIMEOUTSENDERSR = 1
TIEMOUTPORPAQUETESR = 1
## RECIEVE
TIMEOUTRECEIVER = 10


WINDOWCONSTANT = 0.01
WINDOWTHRESHOLD = 1000

FORMATORED = "!I"
FORMATONATIVO = "=I"

MENSAJECONECCION = b"SYN"
# ESTOS TIENEN QUE TENER EL MISMO TAMANO... bueno en realidad no.
# pero hace las cosas ms faciles. 
#MENSAJEUPLOAD = b"UPL"
# MENSAJEDOWNLOAD = b"DOW"
MENSAJEACK = b"ACK"
MENSAJEACEPTARCONECCION= b"SYNACK"


# Packet loss - usar interfaz lo para localhost 
# sudo tc qdisc add dev <interface_name> root netem delay 0 loss 10%

# Para ver que se haya seteado bien
# sudo tc qdisc show dev <interface_name>

# Para sacar el packet loss
# sudo tc qdisc del dev <interface_name> root


class ClientFlags(Enum):
    VERBOSE = "-v"
    VERBOSEL = "--verbose"

    QUIET = "-q"
    QUIETL = "--quiet"
    
    MYIP = "-m"
    MYIPL = "--myIp"

    HELP = "-h"
    HELPL = "--help"

    HOST = "-H"
    HOSTL = "--host"
        
    PORT = "-p"
    PORTL = "--port"
    
    SRC = "-s"
    SRCL = "--src"

    NAME = "-n"
    NAMEL = "--name"

    DST = "-d"
    DSTL = "--dst"

class ServerFlags(Enum):
    VERBOSE = "-v"
    QUIET = "-q"
    HELP = "-h"
    HELPL = "--help"
    HOST = "-H"
    PORT = "-p"
    STORAGE = "-s"

VERBOSE = True
QUIET = False

## SERVER DEFAULT VALUES
DEFAULT_SERVER_IP = "127.0.0.1"
DEFAULT_SERVER_PORT = 5005
DEFAULT_SERVER_STORAGE = "data/server"
DEFAULT_SERVER_VERBOSITY = VERBOSE


### CLIENT DEFAULT VALUES
DEFAULT_CLIENT_IP = "127.0.0.2"
DEFAULT_CLIENT_VERBOSITY = VERBOSE


# COLORS

PINK = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'


"""
    TODO
    correr sin nada y que ande con ips cosas default
    correr con flags y que se seteen bien

    ver como falla con mininet si no seteo nada y corre con default
    ver que ande en mininet si le seteo las ips


    SERVER:
    valores default
        ip = 127.0.0.1
        puerto = 5555

"""

def pretty_print(mensaje:str, is_verbose:bool):    
    if is_verbose == QUIET:
        return
    print(mensaje)