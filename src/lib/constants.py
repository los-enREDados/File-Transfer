IPTUPLA = 0
PUERTOTUPLA = 1

TIPODEPROTOCOLO = "SW" 

# Estos dos estan en bytes
TAMANONUMERORED = 4
TAMANOFIN = 1

# HEADER
TAMANOHEADER = TAMANONUMERORED + TAMANOFIN
TAMANOPAQUETE = 504
FIN = 1
NOFIN = 0


TAMANOLECTURAARCHIVO = None

# TODO: Bajar
TIMEOUTSENDER = 50.0
TIMEOUTSENDER = 500.0

FORMATORED = "!I"
FORMATONATIVO = "=I"

MENSAJECONECCION = b"SYN"
# ESTOS TIENEN QUE TENER EL MISMO TAMANO... bueno en realidad no.
# pero hace las cosas ms faciles. 
MENSAJEUPLOAD = b"UPL"
MENSAJEDOWNLOAD = b"DOW"
MENSAJEACK = b"ACK"
MENSAJEACEPTARCONECCION= b"SYNACK"

