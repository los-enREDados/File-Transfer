# File transfer en UDP

## Comandos

### Correr server
```terminal
make server
```
### Correr upload
```terminal
make ARCHIVO=<nombreArchivo> upload 
```
### Correr download
TBD 

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
make ARCHIVO=<nombreArchivo> crearPerdida
```
### Sacar perdida de paquetes
WARNING: Posiblemente necesita permisos de root
```terminal
make sacarPerdida
```



## Bibliografía
- https://wiki.python.org/moin/UdpCommunication
