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
TAMANOPAQUETE = 500 + TAMANOHEADER


#CONSTATS
UPLOAD = 1
DOWNLOAD = 0
CONNECT = 1
NOCONNECT = 0
FIN = 1
NOFIN = 0
ERROR = 1
NOERROR = 0

TAMANOLECTURAARCHIVO = None

TIMEOUTSENDER = 0.01

# TODO: Bajar. Esto es muy grande; es solo para debugear
TIMEOUTSENDERSR = 1
TIEMOUTPORPAQUETESR = 1

FORMATORED = "!I"
FORMATONATIVO = "=I"

MENSAJECONECCION = b"SYN"
# ESTOS TIENEN QUE TENER EL MISMO TAMANO... bueno en realidad no.
# pero hace las cosas ms faciles. 
#MENSAJEUPLOAD = b"UPL"
#MENSAJEDOWNLOAD = b"DOW"
MENSAJEACK = b"ACK"
MENSAJEACEPTARCONECCION= b"SYNACK"


# Packet loss - usar interfaz lo para localhost 
# sudo tc qdisc add dev <interface_name> root netem delay 0 loss 10%

# Para ver que se haya seteado bien
# sudo tc qdisc show dev <interface_name>

# Para sacar el packet loss
# sudo tc qdisc del dev <interface_name> root

class Mode(Enum):
    NORMAL = 0
    VERBOSE = 1
    QUIET = 2

class ClientFlags(Enum):
    VERBOSE = "-v"
    QUIET = "-q"
    HELP = "-h"
    HOST = "-H"
    PORT = "-p"
    SRC = "-s"
    NAME = "-n"
    DST = "-d"