import service
import sqlite3

# Verificar si el usuario ya existe
def verificar_usuario(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        username = content['username']
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = ?", (username,))
        if cursor.fetchone()[0] > 0:
            return {'status': 'exists', 'message': 'El usuario ya existe.'}
        else:
            return {'status': 'available', 'message': 'El usuario está disponible.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

def procesar_registro(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        username = content['username']
        password = content['password']
        nombre = content['nombre']
        apellido = content['apellido']

        cursor.execute("""
        INSERT INTO usuarios (nombre, apellido, username, contraseña, rol)
        VALUES (?, ?, ?, ?, 'normal')
        """, (nombre, apellido, username, password))
        conn.commit()

        return {'status': 'success', 'message': 'Usuario registrado exitosamente'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

def procesar_login(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        username = content['username']
        password = content['password']

        cursor.execute("""
        SELECT id, rol, fonda_id, estado_reserva
        FROM usuarios
        WHERE username = ? AND contraseña = ?
        """, (username, password))
        result = cursor.fetchone()

        if result:
            usuario_id, role, fonda_id, estado_reserva = result
            response = {
                'status': 'success',
                'message': 'Inicio de sesión exitoso',
                'role': role,
                'usuario_id': usuario_id
            }

            # Incluir fonda_id si es operador
            if role == 'operador':
                response['fonda_id'] = fonda_id

            # Incluir estado_reserva si es usuario normal
            if role == 'normal':
                response['estado_reserva'] = estado_reserva

            return response
        else:
            return {'status': 'failure', 'message': 'Credenciales incorrectas'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

def consultar_estado_reserva(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        usuario_id = content['usuario_id']

        cursor.execute("""
        SELECT estado_reserva
        FROM usuarios
        WHERE id = ?
        """, (usuario_id,))
        estado_reserva = cursor.fetchone()

        if estado_reserva:
            return {'status': 'success', 'estado_reserva': estado_reserva[0]}
        else:
            return {'status': 'failure', 'message': 'Usuario no encontrado.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()




# Servicio principal
def run_service(s: service.Service):
    s.sinit()  # Inicializar el servicio con el bus
    while True:
        request = s.receive()  # Recibir solicitudes del bus
        print("Solicitud recibida:", request.content)  # Depuración

        action = request.content.get('action')
        if action == 'check_user':
            response_content = verificar_usuario(request.content)
        elif action == 'register':
            response_content = procesar_registro(request.content)
        elif action == 'login':
            response_content = procesar_login(request.content)
        elif action == 'check_reservation_status':
            response_content = consultar_estado_reserva(request.content)
        else:
            response_content = {'status': 'failure', 'message': 'Acción no válida'}

        print("Respuesta a enviar:", response_content)  # Depuración
        response = service.Response(s.name, response_content)
        s.send(response)
    s.close()


if __name__ == "__main__":
    s = service.Service('login')  # Nombre del servicio
    run_service(s)
