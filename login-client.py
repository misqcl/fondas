import client
import time

def verificar_usuario(c: client.Client, username):
    # Solicita al servicio verificar si el usuario ya existe
    request_content = {'action': 'check_user', 'username': username}
    request = client.Request('login', request_content)
    c.send(request)  # Enviar solicitud al bus

    response = c.receive()  # Recibir respuesta del bus
    return response.content

def registrar_usuario(c: client.Client):
    print("\n--- Registro de Usuario ---")

    nombre = input("Nombre: ")
    apellido = input("Apellido: ")

    # Verificar nombre de usuario disponible en un bucle
    while True:
        username = input("Nombre de usuario: ")
        response = verificar_usuario(c, username)
        if response.get('status') == 'exists':
            print("Error: El nombre de usuario ya existe. Intenta con otro.")
        else:
            break

    password = input("Contraseña: ")

    request_content = {
        'action': 'register',
        'nombre': nombre,
        'apellido': apellido,
        'username': username,
        'password': password
    }
    request = client.Request('login', request_content)
    c.send(request)  # Enviar solicitud al bus

    response = c.receive()  # Recibir respuesta del bus
    print("Respuesta:", response.content.get('message'))

def crear_fonda(c: client.Client):
    print("\n--- Crear Fonda ---")
    nombre = input("Nombre de la fonda: ")
    mesas = int(input("Cantidad de mesas: "))

    request_content = {
        'action': 'create',
        'nombre': nombre,
        'mesas': mesas
    }
    request = client.Request('fonda', request_content)
    c.send(request)  # Enviar solicitud al bus

    response = c.receive()  # Recibir respuesta del bus
    print("Respuesta:", response.content.get('message'))

def listar_fondas(c: client.Client):
    print("\n--- Listado de Fondas ---")

    request_content = {'action': 'list'}
    request = client.Request('fonda', request_content)
    c.send(request)  # Enviar solicitud al bus

    response = c.receive()  # Recibir respuesta del bus
    if response.content.get('status') == 'success':
        fondas = response.content.get('fondas', [])
        if fondas:
            for f in fondas:
                print(f"ID: {f['id']}, Nombre: {f['nombre']}, Mesas: {f['mesas']}")
        else:
            print("No hay fondas registradas.")
    else:
        print("Error:", response.content.get('message'))

def eliminar_fonda(c: client.Client):
    print("\n--- Eliminar Fonda ---")

    # Solicitar listado de fondas
    request_content = {'action': 'list'}
    request = client.Request('fonda', request_content)
    c.send(request)  # Enviar solicitud al bus

    response = c.receive()  # Recibir respuesta del bus
    if response.content.get('status') == 'success':
        fondas = response.content.get('fondas', [])
        if not fondas:
            print("No hay fondas registradas.")
            return

        # Mostrar lista de fondas con su ID
        print("\nLista de Fondas:")
        for f in fondas:
            print(f"ID: {f['id']}, Nombre: {f['nombre']}, Mesas: {f['mesas']}")

        # Solicitar ID de la fonda a eliminar
        while True:
            try:
                fonda_id = int(input("\nIngrese el ID de la fonda a eliminar: "))
                if any(f['id'] == fonda_id for f in fondas):
                    break
                else:
                    print("El ID ingresado no pertenece a ninguna fonda.")
            except ValueError:
                print("Entrada no válida. Por favor, ingrese un número válido.")

        # Enviar solicitud para eliminar la fonda
        request_content = {'action': 'delete_fonda', 'fonda_id': fonda_id}
        request = client.Request('fonda', request_content)
        c.send(request)  # Enviar solicitud al bus

        response = c.receive()  # Recibir respuesta del bus
        print("Respuesta:", response.content.get('message'))
    else:
        print("Error:", response.content.get('message'))


def crear_operador(c: client.Client):
    print("\n--- Crear Operador ---")
    nombre = input("Nombre del operador: ")
    username = input("Username: ")
    contraseña = input("Contraseña: ")
    fonda_id = int(input("ID de la fonda: "))

    request_content = {
        'action': 'create_operator',
        'nombre': nombre,
        'username': username,
        'contraseña': contraseña,
        'fonda_id': fonda_id
    }
    request = client.Request('opera', request_content)
    c.send(request)  # Enviar solicitud al bus

    response = c.receive()  # Recibir respuesta del bus
    print("Respuesta:", response.content.get('message'))

def ver_ventas(c: client.Client):
    print("\n--- Ver Ventas ---")

    # Solicitar listado de fondas
    request_content = {'action': 'list'}
    request = client.Request('fonda', request_content)
    c.send(request)  # Enviar solicitud al bus

    response = c.receive()  # Recibir respuesta del bus
    if response.content.get('status') == 'success':
        fondas = response.content.get('fondas', [])
        if not fondas:
            print("No hay fondas registradas.")
            return

        # Mostrar lista de fondas disponibles
        print("\nLista de Fondas Disponibles:")
        for f in fondas:
            print(f"ID: {f['id']}, Nombre: {f['nombre']}, Mesas: {f['mesas']}")

        # Solicitar ID de la fonda
        while True:
            try:
                fonda_id = int(input("\nIngrese el ID de la fonda para ver las ventas: "))
                if any(f['id'] == fonda_id for f in fondas):
                    break
                else:
                    print("El ID ingresado no pertenece a ninguna fonda registrada.")
            except ValueError:
                print("Entrada no válida. Por favor, ingrese un número válido.")

        # Solicitar ventas de la fonda
        rango = input("Rango ('diario' o 'semanal'): ").strip().lower()
        request_content = {'action': 'view_sales', 'fonda_id': fonda_id, 'rango': rango}
        request = client.Request('fonda', request_content)
        c.send(request)  # Enviar solicitud al bus

        response = c.receive()  # Recibir respuesta del bus
        if response.content.get('status') == 'success':
            print("Ventas Totales:", response.content.get('total'))
        else:
            print("Error:", response.content.get('message'))
    else:
        print("Error:", response.content.get('message'))


def listar_operadores(c: client.Client):
    print("\n--- Listado de Operadores ---")

    request_content = {'action': 'list_operators'}
    request = client.Request('opera', request_content)
    c.send(request)  # Enviar solicitud al bus

    response = c.receive()  # Recibir respuesta del bus
    if response.content.get('status') == 'success':
        operadores = response.content.get('operadores', [])
        if operadores:
            for o in operadores:
                print(f"ID: {o['id']}, Nombre: {o['nombre']}, Username: {o['username']}, Fonda: {o['fonda']}")
        else:
            print("No hay operadores registrados.")
    else:
        print("Error:", response.content.get('message'))


def eliminar_operador(c: client.Client):
    print("\n--- Eliminar Operador ---")

    # Solicitar listado de operadores
    request_content = {'action': 'list_operators'}
    request = client.Request('opera', request_content)  # Cambiado a 'opera'
    c.send(request)  # Enviar solicitud al bus

    response = c.receive()  # Recibir respuesta del bus
    if response.content.get('status') == 'success':
        operadores = response.content.get('operadores', [])
        if not operadores:
            print("No hay operadores registrados.")
            return

        # Mostrar lista de operadores con su ID
        print("\nLista de Operadores:")
        for o in operadores:
            print(f"ID: {o['id']}, Nombre: {o['nombre']}, Username: {o['username']}, Fonda: {o['fonda']}")

        # Solicitar ID del operador a eliminar
        while True:
            try:
                operador_id = int(input("\nIngrese el ID del operador a eliminar: "))
                if any(o['id'] == operador_id for o in operadores):
                    break
                else:
                    print("El ID ingresado no pertenece a ningún operador.")
            except ValueError:
                print("Entrada no válida. Por favor, ingrese un número válido.")

        # Enviar solicitud para eliminar el operador
        request_content = {'action': 'delete_operator', 'operador_id': operador_id}
        request = client.Request('opera', request_content)  # Cambiado a 'opera'
        c.send(request)  # Enviar solicitud al bus

        response = c.receive()  # Recibir respuesta del bus
        print("Respuesta:", response.content.get('message'))
    else:
        print("Error:", response.content.get('message'))


def menu_admin(c: client.Client):
    while True:
        print("\n--- Menú de Administrador ---")
        print("1. Crear fonda")
        print("2. Ver listado de fondas")
        print("3. Eliminar fonda")
        print("4. Crear operador")
        print("5. Ver listado de operadores")
        print("6. Eliminar operador")
        print("7. Ver ventas")
        print("8. Cerrar sesión")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            crear_fonda(c)
        elif opcion == "2":
            listar_fondas(c)
        elif opcion == "3":
            eliminar_fonda(c)
        elif opcion == "4":
            crear_operador(c)
        elif opcion == "5":
            listar_operadores(c)
        elif opcion == "6":
            eliminar_operador(c)
        elif opcion == "7":
            ver_ventas(c)
        elif opcion == "8":
            print("Cerrando sesión...")
            break
        else:
            print("Opción no válida.")
def iniciar_sesion(c: client.Client):
    print("\n--- Inicio de Sesión ---")
    username = input("Nombre de usuario: ")
    password = input("Contraseña: ")

    request_content = {
        'action': 'login',
        'username': username,
        'password': password
    }
    request = client.Request('login', request_content)
    c.send(request)  # Enviar solicitud al bus

    response = c.receive()  # Recibir respuesta del bus
    if response.content.get('status') == 'success':
        print(response.content.get('message'))
        role = response.content.get('role')
        usuario_id = response.content.get('usuario_id')
        if role == 'admin':
            menu_admin(c)  # Menú del administrador
        elif role == 'operador':
            user_fonda_id = response.content.get('fonda_id')
            if user_fonda_id is not None:
                menu_operador(c, user_fonda_id)  # Pasar fonda_id al menú del operador
            else:
                print("Error: No se encontró el ID de la fonda para este operador.")
        elif role == 'normal':
            while True:
                # Consultar el estado de la reserva directamente desde el servicio de login
                request_content = {'action': 'check_reservation_status', 'usuario_id': usuario_id}
                request = client.Request('login', request_content)
                c.send(request)
                response = c.receive()
                estado_reserva = response.content.get('estado_reserva')

                if estado_reserva == 'activo':
                    print("Esperando a que el operador libere su mesa...")
                    time.sleep(5)  # Esperar antes de consultar nuevamente
                else:
                    menu_usuario(c, usuario_id)
                    break
        else:
            print("Rol no reconocido.")
    else:
        print("Error:", response.content.get('message'))






# Función para gestionar inventario
def gestionar_inventario(c: client.Client, user_fonda_id):
    while True:
        print("\n--- Gestión de Inventario ---")
        print("1. Agregar producto")
        print("2. Actualizar producto")
        print("3. Eliminar producto")
        print("4. Ver inventario")
        print("5. Volver al menú principal")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":  # Agregar producto
            producto = input("Nombre del producto: ")
            cantidad = int(input("Cantidad: "))
            precio = int(input("Precio: "))
            request_content = {'action': 'add', 'producto': producto, 'cantidad': cantidad, 'precio': precio, 'user_fonda_id': user_fonda_id}
            request = client.Request('invnt', request_content)
            c.send(request)
            response = c.receive()
            print("Respuesta:", response.content.get('message', 'Error al procesar la solicitud.'))

        elif opcion == "2":  # Actualizar producto
            print("\n--- Productos Disponibles ---")
            request_content = {'action': 'view', 'user_fonda_id': user_fonda_id}
            request = client.Request('invnt', request_content)
            c.send(request)
            response = c.receive()
            productos = response.content.get('productos', [])
            if productos:
                for p in productos:
                    print(f"Producto: {p['producto']}, Cantidad: {p['cantidad']}, Precio: {p['precio']}")
                producto = input("\nNombre del producto a actualizar: ")
                cantidad = int(input("Nueva cantidad: "))
                precio = int(input("Nuevo precio: "))
                request_content = {'action': 'update', 'producto': producto, 'cantidad': cantidad, 'precio': precio, 'user_fonda_id': user_fonda_id}
                request = client.Request('invnt', request_content)
                c.send(request)
                response = c.receive()
                print("Respuesta:", response.content.get('message', 'Error al procesar la solicitud.'))
            else:
                print("No hay productos disponibles para actualizar.")

        elif opcion == "3":  # Eliminar producto
            print("\n--- Productos Disponibles ---")
            request_content = {'action': 'view', 'user_fonda_id': user_fonda_id}
            request = client.Request('invnt', request_content)
            c.send(request)
            response = c.receive()
            productos = response.content.get('productos', [])
            if productos:
                for p in productos:
                    print(f"Producto: {p['producto']}, Cantidad: {p['cantidad']}, Precio: {p['precio']}")
                producto = input("\nNombre del producto a eliminar: ")
                request_content = {'action': 'delete', 'producto': producto, 'user_fonda_id': user_fonda_id}
                request = client.Request('invnt', request_content)
                c.send(request)
                response = c.receive()
                print("Respuesta:", response.content.get('message', 'Error al procesar la solicitud.'))
            else:
                print("No hay productos disponibles para eliminar.")

        elif opcion == "4":  # Ver inventario
            request_content = {'action': 'view', 'user_fonda_id': user_fonda_id}
            request = client.Request('invnt', request_content)
            c.send(request)
            response = c.receive()
            productos = response.content.get('productos', [])
            if productos:
                print("\n--- Productos en el Inventario ---")
                for p in productos:
                    print(f"Producto: {p['producto']}, Cantidad: {p['cantidad']}, Precio: {p['precio']}")
            else:
                print("No hay productos en el inventario.")


        elif opcion == "5":  # Salir
            break

        else:
            print("Opción no válida.")




# Función para gestionar promociones
# Función para gestionar promociones
def gestionar_promociones(c: client.Client, user_fonda_id):
    while True:
        print("\n--- Gestión de Promociones ---")
        print("1. Agregar promoción")
        print("2. Ver promociones")
        print("3. Volver al menú principal")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            promocion = input("Nombre de la promoción: ")
            cantidad = int(input("Cantidad: "))
            precio = int(input("Precio: "))
            request_content = {
                'action': 'add_promotion',
                'promocion': promocion,
                'cantidad': cantidad,
                'precio': precio,
                'user_fonda_id': user_fonda_id
            }
            request = client.Request('invnt', request_content)
            c.send(request)
        elif opcion == "2":
            request_content = {
                'action': 'view_promotions',
                'user_fonda_id': user_fonda_id
            }
            request = client.Request('invnt', request_content)
            c.send(request)
        elif opcion == "3":
            break
        else:
            print("Opción no válida.")

        # Manejo de respuesta
        response = c.receive()
        if opcion == "1":
            print("Respuesta:", response.content.get('message', 'Error al procesar la solicitud.'))
        elif opcion == "2":
            promociones = response.content.get('promociones', [])
            if promociones:
                print("\n--- Promociones Disponibles ---")
                for p in promociones:
                    print(f"Promoción: {p['promocion']}, Cantidad: {p['cantidad']}, Precio: {p['precio']}")
            else:
                print("No hay promociones registradas.")


def gestionar_mesas(c: client.Client, user_fonda_id):
    while True:
        print("\n--- Gestión de Mesas ---")
        print("1. Ver mesas ocupadas")
        print("2. Liberar una mesa (cobrar cuenta)")
        print("3. Volver al menú principal")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            # Ver mesas ocupadas
            request_content = {'action': 'view_reservations', 'fonda_id': user_fonda_id}
            request = client.Request('mesas', request_content)
            c.send(request)

            response = c.receive()
            reservas = response.content.get('mesas', [])
            if reservas:
                print("\n--- Reservas Pendientes ---")
                for idx, r in enumerate(reservas, start=1):
                    print(f"{idx}. Usuario: {r['cliente']} (ID: {r['usuario_id']}), Personas: {r['personas']}")
            else:
                print(response.content.get('message', 'No hay reservas pendientes.'))

        elif opcion == "2":
            # Liberar mesa
            print("\n--- Liberar Mesa ---")
            request_content = {'action': 'view_reservations', 'fonda_id': user_fonda_id}
            request = client.Request('mesas', request_content)
            c.send(request)

            response = c.receive()
            reservas = response.content.get('mesas', [])
            if not reservas:
                print("No hay reservas pendientes para liberar.")
                continue

            print("\n--- Reservas Pendientes ---")
            for r in reservas:
                print(f"Usuario: {r['cliente']} (ID: {r['usuario_id']}), Personas: {r['personas']}")

            while True:
                try:
                    usuario_id = int(input("\nIngrese el ID del usuario para liberar su mesa, o pulse 0 para cancelar: "))
                    if usuario_id == 0:
                        break
                    if any(r['usuario_id'] == usuario_id for r in reservas):
                        break
                    else:
                        print("ID no válido. Intente nuevamente.")
                except ValueError:
                    print("Entrada no válida. Debe ser un número.")

            if usuario_id == 0:
                continue

            # Obtener inventario completo (productos y promociones)
            request_content = {'action': 'view_all', 'user_fonda_id': user_fonda_id}
            request = client.Request('invnt', request_content)
            c.send(request)

            response = c.receive()
            inventario = response.content.get('inventario', [])
            if not inventario:
                print("No hay inventario disponible.")
                continue

            print("\n--- Inventario Disponible ---")
            for item in inventario:
                categoria = "Promoción" if item['categoria'] == 'promocion' else "Producto"
                print(f"{categoria}: {item['producto']}, Cantidad: {item['cantidad']}, Precio: {item['precio']}")

            # Registrar consumo
            consumo = []
            while True:
                producto = input("\nProducto consumido (o 'listo' para terminar): ")
                if producto.lower() == 'listo':
                    break

                try:
                    cantidad = int(input(f"Cantidad de {producto}: "))
                    consumo.append({'producto': producto, 'cantidad': cantidad})
                except ValueError:
                    print("Por favor, introduzca un número válido para la cantidad.")

            if not consumo:
                print("No se registraron productos consumidos. Operación cancelada.")
                continue

            # Solicitar método de pago
            metodo_pago = input("\nMétodo de pago (efectivo, débito, crédito): ").strip().lower()

            # Enviar solicitud para liberar la mesa
            request_content = {
                'action': 'release_table',
                'usuario_id': usuario_id,
                'fonda_id': user_fonda_id,
                'consumo': consumo,
                'metodo_pago': metodo_pago
            }
            request = client.Request('mesas', request_content)
            c.send(request)

            response = c.receive()
            if response.content.get('status') == 'success':
                print("Respuesta:", response.content.get('message'))

                # Registrar venta en la tabla de ventas
                try:
                    total_venta = sum(item['cantidad'] * next(
                        prod['precio'] for prod in inventario if prod['producto'] == item['producto']
                    ) for item in consumo)

                    venta_request_content = {
                        'action': 'register_sale',
                        'fonda_id': user_fonda_id,
                        'total': total_venta,
                        'metodo_pago': metodo_pago
                    }
                    venta_request = client.Request('stats', venta_request_content)
                    c.send(venta_request)
                    venta_response = c.receive()
                    print(venta_response.content.get('message', 'Venta registrada.'))
                except StopIteration:
                    print("Error: Algunos productos no están disponibles en el inventario.")
            else:
                print("Error:", response.content.get('message'))


        elif opcion == "3":
            # Salir del menú de gestión de mesas
            break

        else:
            print("Opción no válida.")








# Función para gestionar opiniones
# Función para gestionar opiniones
def gestionar_opiniones(c: client.Client, user_fonda_id):
    while True:
        print("\n--- Gestión de Opiniones ---")
        print("1. Ver opiniones")
        print("2. Responder opinión")
        print("3. Volver al menú principal")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            # Ver opiniones
            request_content = {'action': 'view_opinions', 'user_fonda_id': user_fonda_id}
            request = client.Request('opins', request_content)
            c.send(request)

            response = c.receive()
            opiniones = response.content.get('opiniones', [])
            if opiniones:
                print("\n--- Opiniones ---")
                for o in opiniones:
                    print(f"ID: {o['id']}, Cliente: {o['cliente']}, Comentario: {o['comentario']}, "
                          f"Estrellas: {o['estrellas']}, Respuesta: {o['respuesta'] or 'Sin respuesta'}")
            else:
                print("No hay opiniones de momento.")
        elif opcion == "2":
            # Responder opinión
            request_content = {'action': 'view_opinions', 'user_fonda_id': user_fonda_id}
            request = client.Request('opins', request_content)
            c.send(request)

            response = c.receive()
            opiniones = response.content.get('opiniones', [])
            if not opiniones:
                print("No hay opiniones disponibles para responder.")
                continue

            print("\n--- Opiniones ---")
            for o in opiniones:
                print(f"ID: {o['id']}, Cliente: {o['cliente']}, Comentario: {o['comentario']}, "
                      f"Estrellas: {o['estrellas']}, Respuesta: {o['respuesta'] or 'Sin respuesta'}")

            opinion_id = int(input("\nID de la opinión a responder: "))
            respuesta = input("Escriba su respuesta: ")

            request_content = {'action': 'respond_opinion', 'opinion_id': opinion_id, 'respuesta': respuesta}
            request = client.Request('opins', request_content)
            c.send(request)

            response = c.receive()
            print("Respuesta:", response.content.get('message', 'Error al procesar la solicitud.'))
        elif opcion == "3":
            break
        else:
            print("Opción no válida.")


# Función para ver estadísticas
# Función para ver estadísticas
# Función para ver estadísticas
def ver_estadisticas(c: client.Client, user_fonda_id):
    while True:
        print("\n--- Ver Estadísticas ---")
        print("1. Ventas totales")
        print("2. Volver al menú principal")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            while True:
                rango = input("\nIngrese el rango ('diario' o 'semanal', o '0' para volver): ").lower()
                if rango in ['diario', 'semanal']:
                    request_content = {
                        'action': 'view_sales',
                        'rango': rango,
                        'user_fonda_id': user_fonda_id
                    }
                    request = client.Request('stats', request_content)
                    c.send(request)
                    response = c.receive()
                    ventas = response.content.get('ventas', [])
                    if ventas:
                        print("\n--- Ventas ---")
                        for v in ventas:
                            print(f"Fecha: {v['fecha']}, Total: {v['total']}, Método de Pago: {v['metodo_pago']}")
                        print(f"Total general: {sum(v['total'] for v in ventas)}")
                    else:
                        print("No hay datos de ventas para el rango seleccionado.")
                elif rango == '0':
                    break
                else:
                    print("Entrada no válida. Intente nuevamente.")

        
        elif opcion == "2":
            break
        else:
            print("Opción no válida.")




def menu_usuario(c: client.Client, usuario_id):
    while True:
        print("\n--- Menú de Usuario ---")
        print("1. Reservar mesa")
        print("2. Ver listado de fondas y sus calificaciones")
        print("3. Ver mejores promociones")
        print("4. Mis opiniones")
        print("5. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            # Listar fondas disponibles
            request_content = {'action': 'list'}
            request = client.Request('fonda', request_content)
            c.send(request)

            response = c.receive()
            fondas = response.content.get('fondas', [])
            if not fondas:
                print("No hay fondas disponibles.")
                continue

            print("\n--- Fondas Disponibles ---")
            for idx, f in enumerate(fondas, start=1):  # Mostrar lista numerada para claridad
                print(f"{idx}. {f['nombre']} ({f['calificacion']} estrellas) - Mesas: {f['mesas']}")

            while True:
                try:
                    opcion_fonda = int(input("\nSeleccione el número de la fonda o pulse 0 para cancelar: ")) - 1
                    if opcion_fonda == -1:  # Opción para cancelar
                        print("Operación cancelada.")
                        break
                    if 0 <= opcion_fonda < len(fondas):
                        fonda_id = fondas[opcion_fonda]['id']
                        fonda_nombre = fondas[opcion_fonda]['nombre']
                        break
                    else:
                        print("Número no válido. Intente nuevamente.")
                except ValueError:
                    print("Entrada no válida. Debe ser un número.")

            if opcion_fonda == -1:
                continue

            personas = int(input("¿Cuántas personas son? "))
            print(f"\nSeguro que deseas reservar en '{fonda_nombre}' para {personas} personas?")
            confirmacion = input("Confirma con 'S' para continuar o 'N' para cancelar: ").lower()

            if confirmacion == 's':
                request_content = {
                    'action': 'reserve',
                    'usuario_id': usuario_id,
                    'fonda_id': fonda_id,
                    'personas': personas
                }
                request = client.Request('mesas', request_content)
                c.send(request)

                response = c.receive()
                if response.content.get('status') != 'success':
                    print("Error al reservar mesa:", response.content.get('message'))
                    continue

                print("\nReserva confirmada. Esperando a que el operador libere tu mesa...")

                # Bloquear el sistema en modo de espera hasta que la mesa sea liberada
                while True:
                    time.sleep(5)  # Esperar 5 segundos antes de consultar nuevamente

                    # Consultar el estado de la reserva
                    request_content = {'action': 'check_reservation_status', 'usuario_id': usuario_id}
                    request = client.Request('mesas', request_content)
                    c.send(request)
                    response = c.receive()

                    if response.content.get('status') != 'success':
                        print("\nError en la comunicación con el servidor:", response.content.get('message'))
                        break

                    estado_reserva = response.content.get('estado_reserva', 'desconocido')

                    if estado_reserva == 'libre':
                        print("\nTu mesa ha sido liberada. ¡Disfruta tu visita!")
                        break
                    elif estado_reserva == 'pendiente' or estado_reserva == 'activo':
                        print("\nLa mesa sigue reservada. Por favor, espera...")
                    else:
                        print("\nGracias por visitarnos, recuerda que puedes dejar tu opinión.")
                        break



        elif opcion == "2":
            # Ver listado de fondas con calificaciones
            request_content = {'action': 'list'}
            request = client.Request('fonda', request_content)
            c.send(request)

            response = c.receive()
            fondas = response.content.get('fondas', [])
            if not fondas:
                print("No hay fondas disponibles.")
            else:
                print("\n--- Fondas Disponibles ---")
                for f in fondas:
                    print(f"{f['nombre']} ({f['calificacion']} estrellas) - Mesas: {f['mesas']}")

        elif opcion == "3":  # Ver mejores promociones globales
            request_content = {'action': 'view_best_promotions'}
            request = client.Request('invnt', request_content)
            c.send(request)

            response = c.receive()
            promociones = response.content.get('promociones', [])
            if not promociones:
                print("No hay promociones disponibles.")
            else:
                print("\n--- Mejores Promociones ---")
                for p in promociones:
                    print(f"{p['promocion']} - {p['precio']} pesos (Fonda: {p['fonda']})")



        elif opcion == "4":
            # Ver mis opiniones y fondas visitadas
            request_content = {'action': 'visited_fondas_with_opinions', 'usuario_id': usuario_id}
            request = client.Request('opins', request_content)
            c.send(request)

            response = c.receive()
            fondas = response.content.get('fondas', [])

            if not fondas:
                print("No has visitado fondas aún, visita alguna para poder opinar.")
            else:
                print("\n--- Fondas Visitadas ---")
                for idx, f in enumerate(fondas, start=1):
                    print(f"{idx}. {f['nombre']} ({f['calificacion']} estrellas)")
                    if f['opinion']:
                        print(f"    Mi opinión: {f['opinion']['comentario']} ({f['opinion']['estrellas']} estrellas)")
                        print(f"    Respuesta Admin: {f['opinion']['respuesta'] or 'Sin respuesta'}")
                    else:
                        print("    No has dejado una opinión para esta fonda.")

                while True:
                    try:
                        seleccion = int(input("\nSelecciona una fonda de la lista para gestionar tu opinión, o pulsa 0 para volver: "))
                        if seleccion == 0:
                            break
                        if 1 <= seleccion <= len(fondas):
                            fonda_id = fondas[seleccion - 1]['id']
                            break
                        else:
                            print("Selección no válida. Inténtalo de nuevo.")
                    except ValueError:
                        print("Entrada no válida. Inténtalo de nuevo.")

                if seleccion == 0:
                    continue

                print("\n--- Opciones de Opinión ---")
                print("1. Dejar una nueva opinión")
                print("2. Editar una opinión existente")
                print("3. Eliminar una opinión existente")
                opinion_opcion = input("Selecciona una opción: ")

                if opinion_opcion == "1":
                    # Dejar una nueva opinión
                    comentario = input("Escribe tu comentario: ")
                    while True:
                        try:
                            estrellas = int(input("Califica la fonda (1-5 estrellas): "))
                            if 1 <= estrellas <= 5:
                                break
                            else:
                                print("Por favor, introduce un número entre 1 y 5.")
                        except ValueError:
                            print("Entrada no válida. Inténtalo de nuevo.")

                    request_content = {
                        'action': 'add_opinion',
                        'usuario_id': usuario_id,
                        'fonda_id': fonda_id,
                        'comentario': comentario,
                        'estrellas': estrellas
                    }
                    request = client.Request('opins', request_content)
                    c.send(request)
                    response = c.receive()
                    print(response.content.get('message'))

                elif opinion_opcion == "2":
                    # Editar una opinión existente
                    comentario = input("Escribe tu nuevo comentario: ")
                    while True:
                        try:
                            estrellas = int(input("Recalifica la fonda (1-5 estrellas): "))
                            if 1 <= estrellas <= 5:
                                break
                            else:
                                print("Por favor, introduce un número entre 1 y 5.")
                        except ValueError:
                            print("Entrada no válida. Inténtalo de nuevo.")

                    request_content = {
                        'action': 'edit_opinion',
                        'usuario_id': usuario_id,
                        'fonda_id': fonda_id,
                        'comentario': comentario,
                        'estrellas': estrellas
                    }
                    request = client.Request('opins', request_content)
                    c.send(request)
                    response = c.receive()
                    print(response.content.get('message'))

                elif opinion_opcion == "3":
                    # Eliminar una opinión existente
                    confirmacion = input("¿Estás seguro de que deseas eliminar tu opinión? (s/n): ").lower()
                    if confirmacion == "s":
                        request_content = {
                            'action': 'delete_opinion',
                            'usuario_id': usuario_id,
                            'fonda_id': fonda_id
                        }
                        request = client.Request('opins', request_content)
                        c.send(request)
                        response = c.receive()
                        print(response.content.get('message'))
                    else:
                        print("Operación cancelada.")



        elif opcion == "5":
            print("Saliendo...")
            break
        else:
            print("Opción no válida.")






# Menú principal del operador
def menu_operador(c: client.Client, user_fonda_id):
    while True:
        print("\n--- Menú de Operador ---")
        print("1. Gestionar inventario")
        print("2. Gestionar promociones")
        print("3. Gestionar mesas")
        print("4. Gestionar opiniones")
        print("5. Ver estadísticas")
        print("6. Cerrar sesión")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            gestionar_inventario(c, user_fonda_id)
        elif opcion == "2":
            gestionar_promociones(c, user_fonda_id)
        elif opcion == "3":
            gestionar_mesas(c, user_fonda_id)
        elif opcion == "4":
            gestionar_opiniones(c, user_fonda_id)
        elif opcion == "5":
            ver_estadisticas(c, user_fonda_id)
        elif opcion == "6":
            print("Cerrando sesión...")
            break
        else:
            print("Opción no válida.")
def menu_normal():
    c = client.Client()  # Conectar al bus
    while True:
        print("\n--- Menú Principal ---")
        print("1. Registrar usuario")
        print("2. Iniciar sesión")
        print("3. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_usuario(c)
        elif opcion == "2":
            iniciar_sesion(c)
        elif opcion == "3":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida.")
    c.close()

if __name__ == "__main__":
    menu_normal()
