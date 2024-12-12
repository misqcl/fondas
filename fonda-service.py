import service
import sqlite3
from datetime import datetime, timedelta

# Crear una fonda y sus mesas
def crear_fonda(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        nombre = content['nombre']
        mesas = content['mesas']

        # Verify if the fonda already exists
        cursor.execute("SELECT COUNT(*) FROM fondas WHERE nombre = ?", (nombre,))
        if cursor.fetchone()[0] > 0:
            return {'status': 'failure', 'message': 'La fonda ya existe.'}

        # Create the fonda
        cursor.execute("INSERT INTO fondas (nombre, mesas) VALUES (?, ?)", (nombre, mesas))
        fonda_id = cursor.lastrowid

        # Populate mesas table
        for i in range(1, mesas + 1):
            cursor.execute("INSERT INTO mesas (fonda_id, numero, estado) VALUES (?, ?, 'disponible')", (fonda_id, i))

        conn.commit()
        return {'status': 'success', 'message': 'Fonda creada exitosamente.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()


# Listar fondas
def listar_fondas(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT f.id, f.nombre, f.mesas, AVG(o.estrellas) as calificacion
        FROM fondas f
        LEFT JOIN opiniones o ON f.id = o.fonda_id
        GROUP BY f.id, f.nombre, f.mesas
        """)
        fondas = cursor.fetchall()

        if fondas:
            return {'status': 'success', 'fondas': [
                {'id': f[0], 'nombre': f[1], 'mesas': f[2], 'calificacion': f[3] or 0} for f in fondas
            ]}
        else:
            return {'status': 'success', 'fondas': []}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

# Eliminar fonda y sus mesas
def eliminar_fonda(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        fonda_id = content['fonda_id']

        # Verificar si la fonda existe
        cursor.execute("SELECT COUNT(*) FROM fondas WHERE id = ?", (fonda_id,))
        if cursor.fetchone()[0] == 0:
            return {'status': 'failure', 'message': 'La fonda no existe.'}

        # Eliminar las mesas asociadas a la fonda
        cursor.execute("DELETE FROM mesas WHERE fonda_id = ?", (fonda_id,))

        # Eliminar la fonda
        cursor.execute("DELETE FROM fondas WHERE id = ?", (fonda_id,))
        conn.commit()

        return {'status': 'success', 'message': 'Fonda y sus mesas eliminadas exitosamente.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

# Ver ventas totales
def ver_ventas(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        fonda_id = content['fonda_id']
        rango = content['rango']  # 'diario' o 'semanal'

        # Verificar si la fonda existe
        cursor.execute("SELECT COUNT(*) FROM fondas WHERE id = ?", (fonda_id,))
        if cursor.fetchone()[0] == 0:
            return {'status': 'failure', 'message': 'La fonda no existe.'}

        # Determinar el rango de fechas
        hoy = datetime.now()
        if rango == 'diario':
            fecha_inicio = hoy
        elif rango == 'semanal':
            fecha_inicio = hoy - timedelta(days=7)

        # Calcular las ventas
        cursor.execute("""
        SELECT SUM(total) FROM ventas
        WHERE fonda_id = ? AND fecha >= ?
        """, (fonda_id, fecha_inicio.strftime('%Y-%m-%d')))
        total = cursor.fetchone()[0] or 0

        return {'status': 'success', 'total': total}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

# Obtener opiniones de una fonda
def opiniones_fonda(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        fonda_id = content['fonda_id']

        # Obtener opiniones de la fonda
        cursor.execute("""
        SELECT u.nombre || ' ' || u.apellido AS cliente, o.comentario, o.estrellas, o.respuesta
        FROM opiniones o
        JOIN usuarios u ON o.usuario_id = u.id
        WHERE o.fonda_id = ?
        """, (fonda_id,))
        opiniones = cursor.fetchall()

        return {'status': 'success', 'opiniones': [
            {'cliente': o[0], 'comentario': o[1], 'estrellas': o[2], 'respuesta': o[3] or ''}
            for o in opiniones
        ]}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

# Listar usuarios
def listar_usuarios(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, nombre, apellido, fonda_id, rol FROM usuarios")
        users = cursor.fetchall()

        if users:
            return {'status': 'success', 'users': [{'id': f[0], 'nombre': f[1], 'apellido': f[2], 'fonda_id': f[3], 'rol': f[4]} for f in users]}
        else:
            return {'status': 'success', 'users': []}
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
        if action == 'create':
            response_content = crear_fonda(request.content)
        elif action == 'list':
            response_content = listar_fondas(request.content)
        elif action == 'delete_fonda':
            response_content = eliminar_fonda(request.content)
        elif action == 'view_sales':
            response_content = ver_ventas(request.content)
        elif action == 'all_users':
            response_content = listar_usuarios(request.content)
        elif action == 'view_opinions':
            response_content = opiniones_fonda(request.content)
        else:
            response_content = {'status': 'failure', 'message': 'Acción no válida'}

        print("Respuesta a enviar:", response_content)  # Depuración
        response = service.Response(s.name, response_content)
        s.send(response)
    s.close()

if __name__ == "__main__":
    s = service.Service('fonda')  # Nombre del servicio
    run_service(s)
