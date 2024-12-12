import sqlite3
import service
# Opiniones ya registradas por el usuario
def opiniones_usuario(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        usuario_id = content['usuario_id']
        cursor.execute("""
        SELECT f.nombre, o.comentario, o.estrellas
        FROM opiniones o
        JOIN fondas f ON o.fonda_id = f.id
        WHERE o.usuario_id = ?
        """, (usuario_id,))
        opiniones = cursor.fetchall()

        return {'status': 'success', 'opiniones': [
            {'fonda': o[0], 'comentario': o[1], 'estrellas': o[2]} for o in opiniones
        ]}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

# Fondas pendientes de opinión
def view_pending_opinions(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        usuario_id = content['usuario_id']
        cursor.execute("""
        SELECT f.id, f.nombre
        FROM reservas r
        JOIN fondas f ON r.fonda_id = f.id
        WHERE r.usuario_id = ? AND r.estado = 'completada'
        AND NOT EXISTS (
            SELECT 1 FROM opiniones o WHERE o.usuario_id = r.usuario_id AND o.fonda_id = r.fonda_id
        )
        """, (usuario_id,))
        pendientes = cursor.fetchall()

        return {'status': 'success', 'fondas': [
            {'fonda_id': p[0], 'nombre': p[1]} for p in pendientes
        ]}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

# Registrar una opinión
def agregar_opinion(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        usuario_id = content['usuario_id']
        fonda_id = content['fonda_id']

        # Verificar si ya existe una opinión
        cursor.execute("""
        SELECT 1 FROM opiniones WHERE usuario_id = ? AND fonda_id = ?
        """, (usuario_id, fonda_id))
        if cursor.fetchone():
            return {'status': 'failure', 'message': 'Ya ha dejado una opinión para esta fonda.'}

        # Insertar la opinión
        comentario = content['comentario']
        estrellas = content['estrellas']
        cursor.execute("""
        INSERT INTO opiniones (usuario_id, fonda_id, comentario, estrellas)
        VALUES (?, ?, ?, ?)
        """, (usuario_id, fonda_id, comentario, estrellas))
        conn.commit()

        return {'status': 'success', 'message': 'Opinión registrada exitosamente.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

def fondas_visitadas(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        usuario_id = content['usuario_id']
        cursor.execute("""
        SELECT DISTINCT f.id, f.nombre, 
               COALESCE(AVG(o.estrellas), 0) AS calificacion
        FROM reservas r
        JOIN fondas f ON r.fonda_id = f.id
        LEFT JOIN opiniones o ON o.fonda_id = f.id
        WHERE r.usuario_id = ? AND r.estado = 'completada'
        GROUP BY f.id, f.nombre
        """, (usuario_id,))
        fondas = cursor.fetchall()

        return {'status': 'success', 'fondas': [
            {'id': f[0], 'nombre': f[1], 'calificacion': round(f[2], 1)} for f in fondas
        ]}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

def editar_opinion(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        usuario_id = content['usuario_id']
        fonda_id = content['fonda_id']
        comentario = content['comentario']
        estrellas = content['estrellas']

        cursor.execute("""
        UPDATE opiniones
        SET comentario = ?, estrellas = ?
        WHERE usuario_id = ? AND fonda_id = ?
        """, (comentario, estrellas, usuario_id, fonda_id))
        conn.commit()

        if cursor.rowcount > 0:
            return {'status': 'success', 'message': 'Opinión actualizada exitosamente.'}
        else:
            return {'status': 'failure', 'message': 'No se encontró una opinión para actualizar.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

def eliminar_opinion(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        usuario_id = content['usuario_id']
        fonda_id = content['fonda_id']

        cursor.execute("""
        DELETE FROM opiniones
        WHERE usuario_id = ? AND fonda_id = ?
        """, (usuario_id, fonda_id))
        conn.commit()

        if cursor.rowcount > 0:
            return {'status': 'success', 'message': 'Opinión eliminada exitosamente.'}
        else:
            return {'status': 'failure', 'message': 'No se encontró una opinión para eliminar.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

def view_opinions(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        user_fonda_id = content['user_fonda_id']

        # Obtener opiniones de la fonda
        cursor.execute("""
        SELECT o.id, u.nombre || ' ' || u.apellido AS cliente, o.comentario, o.estrellas, o.respuesta
        FROM opiniones o
        JOIN usuarios u ON o.usuario_id = u.id
        WHERE o.fonda_id = ?
        """, (user_fonda_id,))
        opiniones = cursor.fetchall()

        return {'status': 'success', 'opiniones': [
            {
                'id': o[0],
                'cliente': o[1],
                'comentario': o[2],
                'estrellas': o[3],
                'respuesta': o[4] or "Sin respuesta"
            } for o in opiniones
        ]}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

def respond_opinion(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        opinion_id = content['opinion_id']
        respuesta = content['respuesta']

        # Actualizar la respuesta de la opinión
        cursor.execute("""
        UPDATE opiniones
        SET respuesta = ?
        WHERE id = ?
        """, (respuesta, opinion_id))
        conn.commit()

        if cursor.rowcount > 0:
            return {'status': 'success', 'message': 'Respuesta enviada exitosamente.'}
        else:
            return {'status': 'failure', 'message': 'Opinión no encontrada.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()
def visited_fondas_with_opinions(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        usuario_id = content['usuario_id']

        cursor.execute("""
        SELECT DISTINCT f.id, f.nombre, 
               COALESCE(AVG(o.estrellas), 0) AS calificacion,
               (SELECT o.comentario FROM opiniones o WHERE o.usuario_id = ? AND o.fonda_id = f.id) AS comentario,
               (SELECT o.estrellas FROM opiniones o WHERE o.usuario_id = ? AND o.fonda_id = f.id) AS estrellas,
               (SELECT o.respuesta FROM opiniones o WHERE o.usuario_id = ? AND o.fonda_id = f.id) AS respuesta
        FROM reservas r
        JOIN fondas f ON r.fonda_id = f.id
        LEFT JOIN opiniones o ON o.fonda_id = f.id
        WHERE r.usuario_id = ? AND r.estado = 'completada'
        GROUP BY f.id, f.nombre
        """, (usuario_id, usuario_id, usuario_id, usuario_id))
        fondas = cursor.fetchall()

        return {'status': 'success', 'fondas': [
            {
                'id': f[0],
                'nombre': f[1],
                'calificacion': round(f[2], 1),
                'opinion': {
                    'comentario': f[3],
                    'estrellas': f[4],
                    'respuesta': f[5]
                } if f[3] else None
            } for f in fondas
        ]}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()


# Servicio principal
def run_service(s: service.Service):
    s.sinit()  # Inicializar el servicio
    while True:
        request = s.receive()  # Recibir solicitudes
        print("Solicitud recibida:", request.content)

        action = request.content.get('action')
        if action == 'my_opinions':
            response_content = opiniones_usuario(request.content)
        elif action == 'visited_fondas':
            response_content = fondas_visitadas(request.content)
        elif action == 'add_opinion':
            response_content = agregar_opinion(request.content)
        elif action == 'edit_opinion':
            response_content = editar_opinion(request.content)
        elif action == 'delete_opinion':
            response_content = eliminar_opinion(request.content)
        elif action == 'view_opinions':
            response_content = view_opinions(request.content)
        elif action == 'respond_opinion':
            response_content = respond_opinion(request.content)
        elif action == 'visited_fondas_with_opinions':
            response_content = visited_fondas_with_opinions(request.content)
        else:
            response_content = {'status': 'failure', 'message': 'Acción no válida'}

        response = service.Response(s.name, response_content)
        s.send(response)
    s.close()


if __name__ == "__main__":
    s = service.Service('opins')
    run_service(s)
