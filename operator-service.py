import service
import sqlite3

# Crear un operador
def crear_operador(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        nombre = content['nombre']
        username = content['username']
        contraseña = content['contraseña']
        fonda_id = content['fonda_id']

        # Verificar que la fonda exista
        cursor.execute("SELECT COUNT(*) FROM fondas WHERE id = ?", (fonda_id,))
        if cursor.fetchone()[0] == 0:
            return {'status': 'failure', 'message': 'La fonda no existe.'}

        # Crear operador
        cursor.execute("""
        INSERT INTO usuarios (nombre, apellido, username, contraseña, rol, fonda_id)
        VALUES (?, '', ?, ?, 'operador', ?)
        """, (nombre, username, contraseña, fonda_id))
        conn.commit()

        return {'status': 'success', 'message': 'Operador creado exitosamente.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

# Listar operadores con su fonda
def listar_operadores(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT usuarios.id, usuarios.nombre, usuarios.username, fondas.nombre AS fonda
        FROM usuarios
        LEFT JOIN fondas ON usuarios.fonda_id = fondas.id
        WHERE usuarios.rol = 'operador'
        """)
        operadores = cursor.fetchall()

        if operadores:
            return {'status': 'success', 'operadores': [
                {'id': o[0], 'nombre': o[1], 'username': o[2], 'fonda': o[3]} for o in operadores
            ]}
        else:
            return {'status': 'success', 'operadores': []}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

# Eliminar operador
def eliminar_operador(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        operador_id = content['operador_id']

        # Eliminar operador
        cursor.execute("DELETE FROM usuarios WHERE id = ? AND rol = 'operador'", (operador_id,))
        conn.commit()

        if cursor.rowcount > 0:
            return {'status': 'success', 'message': 'Operador eliminado exitosamente.'}
        else:
            return {'status': 'failure', 'message': 'Operador no encontrado.'}
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
        if action == 'create_operator':
            response_content = crear_operador(request.content)
        elif action == 'list_operators':
            response_content = listar_operadores(request.content)
        elif action == 'delete_operator':
            response_content = eliminar_operador(request.content)
        else:
            response_content = {'status': 'failure', 'message': 'Acción no válida'}

        print("Respuesta a enviar:", response_content)  # Depuración
        response = service.Response(s.name, response_content)
        s.send(response)
    s.close()

if __name__ == "__main__":
    s = service.Service('opera')  # Nombre del servicio
    run_service(s)
