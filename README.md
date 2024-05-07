# Introducción a los Sistemas Distribuidos (75.43) 


# Trabajo Practico N◦1: File Transfer en UDP

## Como correr el programa

Se asume que se esta en el directorio raíz del proyecto

### Server
```
python3 src/server.py [flags]
```
O también (esta opción no admite flags)
```terminal
make server
```

Por defecto el server corre en 127.0.0.1 en el puerto 5005.

Para especificar la IP y puerto deseadas, usar flags -H y -p.

Para ver mas opciones usar -h.

### Cliente
#### Upload
```
python3 src/upload.py -s ruta/del/archivo -n nombreDelArchivo [flags]
```
O también (usa como ruta por defecto `data/archivosExpo/`, no admite flags)
```terminal
make ARCHIVO=<nombreArchivo> upload 
```

#### Download
```
python3 src/download.py -n nombreDelArchivo [flags]
```
O también (no admite flags):
```terminal
make download ARCHIVO=<nombreArchivo>
```

Por defecto el cliente se intentara conectar al server en
127.0.0.1:5005.

Para cambiar estos valores, usar flags -H y -p.

Para ver mas opciones usar -h.

## Opciones adicionales
### Cambiar modalidad a Selective Repeat
```terminal
make selectiveRepeat
```

### Cambiar modalidad a Stop and Wait
```terminal
make stopAndWait
```

### Introducir perdida artificial de paquetes
WARNING: Posiblemente necesita permisos de root
```terminal
make PERDIDA=<porcentaje> crearPerdida
```
Si no se pasa perdida, se crea una perdida del 10 por cierto por defecto.

### Sacar perdida de paquetes
WARNING: Posiblemente necesita permisos de root
```terminal
make sacarPerdida
```

### Ver la perdida actual
```make
make mostrarPerdida
```

### Mininet
Para correr mininet con la topología ya configurada:

WARNING: Posiblemente necesita permisos de root
```
mn --custom src/lib/mininet.py --topo mytopo
```

La topología consta de 4 hosts y 1 switch. Los hosts son h1, h2, h3 y h4. El switch es s1.

Hay perdida configuarada entre s1 y h3 de 10% y entre s1 y h4 de 40%.

## Bibliografía
- https://wiki.python.org/moin/UdpCommunication

