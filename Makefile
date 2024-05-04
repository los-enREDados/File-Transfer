LOOPBACK    := $(shell ls -l /sys/class/net/ | grep virtual | grep -v docker | awk '{ print $$NF }' | awk -F '/' '{ print $$NF }')
PERDIDA     := 50
ARCHIVO     := data/archivosParaEnviar/azul.jpeg
INTERPRETER := python3

ifeq ("$(RELEASE)", "debug")
INTERPRETER = pudb
endif

stopAndWait:
	sed -i 's/TIPODEPROTOCOLO = ".."/TIPODEPROTOCOLO = "SW"/' src/lib/constants.py

selectiveRepeat:
	sed -i 's/TIPODEPROTOCOLO = ".."/TIPODEPROTOCOLO = "SR"/' src/lib/constants.py

flake8:
	@echo -----------------------------------------------------
	flake8  --exit-zero src/

# Si algun cliente de python quedo colgado, lo mato
matarColgados:
	killall -9 python3

upload:
	$(INTERPRETER) src/upload.py $(ARCHIVO)

server:
	$(INTERPRETER) src/server.py


crearPerdida:
	tc qdisc add dev $(LOOPBACK) root netem delay 0 loss $(PERDIDA)

sacarPerdida:
	tc qdisc del dev $(LOOPBACK) root


.PHONY: server upload download
