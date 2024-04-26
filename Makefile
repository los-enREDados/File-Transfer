LOOPBACK := $(shell ls -l /sys/class/net/ | grep virtual | awk '{ print $$NF }' | awk -F '/' '{ print $$NF }')
PERDIDA  := 50
ARCHIVO  := data/azul.jpeg

stopAndWait:
	sed -i 's/TIPODEPROTOCOLO = ".."/TIPODEPROTOCOLO = "SW"/' src/lib/constants.py

selectiveRepeat:
	sed -i 's/TIPODEPROTOCOLO = ".."/TIPODEPROTOCOLO = "SR"/' src/lib/constants.py

flake8:
	@echo -----------------------------------------------------
	flake8  --exit-zero *.py lib/

# Si algun cliente de python quedo colgado, lo mato
matarColgados:
	killall -9 python3

upload:
	python3 src/upload.py $(ARCHIVO)

server:
	python3 src/server.py


crearPerdida: sacarPerdida
	tc qdisc add dev $(LOOPBACK) root netem delay 0 loss $(PERDIDA)

sacarPerdida:
	tc qdisc del dev $(LOOPBACK) root


.PHONY: server upload download
