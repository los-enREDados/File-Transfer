stopAndWait:
	sed -i 's/TIPODEPROTOCOLO = ".."/TIPODEPROTOCOLO = "SW"/' lib/constants.py

selectiveRepeat:
	sed -i 's/TIPODEPROTOCOLO = ".."/TIPODEPROTOCOLO = "SR"/' lib/constants.py

flake8:
	@echo -----------------------------------------------------
	flake8  --exit-zero *.py lib/

# Si algun cliente de python quedo colgado, lo mato
matarColgados:
	killall -9 python3

cliente:
	python3 src/cliente.py

server:
	python3 src/server.py
