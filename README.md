# fondas

Primero es necesario incializar el BUS docker run -d -p 5000:5000 --name soabus jrgiadach/soabus:v1

Luego inicializamos todos los servicios con python3 por ejemplo : python3 registro-service.py

Existe un cliente general llamado login-client el cual contiene el menu y se inicializa luego de tener todos los servicios habilitados, en caso contrario puede cerrarse o arrojar que no funciona tal servicio

Falta implementar menu usuario y mitad de operador de momento.
