import service
import sqlite3

# Reservar mesa
def reservar_mesa(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        usuario_id = content['usuario_id']
        fonda_id = content['fonda_id']
        personas = content['personas']

        # Calcular mesas necesarias (redondear hacia arriba)
        mesas_necesarias = -(-personas // 4)

        # Verificar mesas disponibles en la tabla 'mesas'
        cursor.execute("""
        SELECT id FROM mesas
        WHERE fonda_id = ? AND estado = 'disponible'
        LIMIT ?
        """, (fonda_id, mesas_necesarias))
        mesas_disponibles = cursor.fetchall()

        if len(mesas_disponibles) < mesas_necesarias:
            return {'status': 'failure', 'message': 'No hay suficientes mesas disponibles para la reserva.'}

        # Actualizar estado de las mesas ocupadas
        mesa_ids = [m[0] for m in mesas_disponibles]
        cursor.execute(f"""
        UPDATE mesas
        SET estado = 'ocupada'
        WHERE id IN ({','.join(['?'] * len(mesa_ids))})
        """, mesa_ids)

        # Registrar la reserva en la tabla 'reservas' con las mesas asociadas
        for mesa_id in mesa_ids:
            cursor.execute("""
            INSERT INTO reservas (usuario_id, fonda_id, personas, mesa_id)
            VALUES (?, ?, ?, ?)
            """, (usuario_id, fonda_id, personas, mesa_id))


        # Actualizar el estado del usuario a 'activo'
        cursor.execute("""
        UPDATE usuarios
        SET estado_reserva = 'activo'
        WHERE id = ?
        """, (usuario_id,))

        conn.commit()

        return {'status': 'success', 'message': f'Reserva realizada con éxito para {mesas_necesarias} mesas.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()


def ver_mesas_ocupadas(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        fonda_id = content['fonda_id']

        # Fetch tables and their reservation status
        cursor.execute("""
        SELECT m.numero, u.nombre || ' ' || u.apellido AS cliente, r.personas, u.id AS usuario_id
        FROM mesas m
        LEFT JOIN reservas r ON m.id = r.mesa_id AND r.estado = 'pendiente'
        LEFT JOIN usuarios u ON r.usuario_id = u.id
        WHERE m.fonda_id = ? AND m.estado = 'ocupada'
        """, (fonda_id,))
        mesas = cursor.fetchall()

        if mesas:
            return {
                'status': 'success',
                'mesas': [{'numero': m[0], 'cliente': m[1], 'personas': m[2], 'usuario_id': m[3]} for m in mesas]
            }
        else:
            return {'status': 'success', 'mesas': [], 'message': 'No hay mesas ocupadas.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()




# Liberar mesa
def liberar_mesa(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        usuario_id = content['usuario_id']
        fonda_id = content['fonda_id']
        consumo = content['consumo']
        metodo_pago = content['metodo_pago']

        cursor.execute("""
        SELECT mesa_id FROM reservas
        WHERE fonda_id = ? AND usuario_id = ? AND estado = 'pendiente'
        """, (fonda_id, usuario_id))
        mesas_ocupadas = cursor.fetchall()


        if not mesas_ocupadas:
            return {'status': 'failure', 'message': 'No hay mesas ocupadas por este usuario.'}

        # Liberar las mesas ocupadas por el usuario
        mesa_ids = [m[0] for m in mesas_ocupadas]
        cursor.execute(f"""
        UPDATE mesas
        SET estado = 'disponible'
        WHERE id IN ({','.join(['?'] * len(mesa_ids))})
        """, mesa_ids)

        conn.commit()

        # Registrar consumo en inventario
        for item in consumo:
            producto = item['producto']
            cantidad = item['cantidad']

            cursor.execute("""
            UPDATE inventario
            SET cantidad = cantidad - ?
            WHERE fonda_id = ? AND producto = ?
            """, (cantidad, fonda_id, producto))
            conn.commit()

        # Cambiar el estado de la reserva a 'completada'
        cursor.execute("""
        UPDATE reservas
        SET estado = 'completada'
        WHERE usuario_id = ? AND fonda_id = ?
        """, (usuario_id, fonda_id))
        conn.commit()

        # Cambiar el estado del usuario a 'libre'
        cursor.execute("""
        UPDATE usuarios
        SET estado_reserva = 'libre'
        WHERE id = ?
        """, (usuario_id,))
        conn.commit()

        return {'status': 'success', 'message': 'Mesa liberada y consumo registrado.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()


def check_reservation_status(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        usuario_id = content['usuario_id']

        # Verificar estado de la reserva
        cursor.execute("""
        SELECT estado
        FROM reservas
        WHERE usuario_id = ? AND estado IN ('pendiente', 'activo', 'libre')
        ORDER BY id DESC LIMIT 1
        """, (usuario_id,))
        reserva = cursor.fetchone()

        if reserva:
            return {'status': 'success', 'estado_reserva': reserva[0]}
        else:
            return {'status': 'success', 'estado_reserva': 'ninguna'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()





    # Obtener reservas pendientes
def listar_reservas_pendientes(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        fonda_id = content['fonda_id']
        cursor.execute("""
        SELECT r.usuario_id, u.nombre || ' ' || u.apellido AS cliente, r.personas
        FROM reservas r
        JOIN usuarios u ON r.usuario_id = u.id
        WHERE r.fonda_id = ? AND r.estado = 'pendiente'
        """, (fonda_id,))
        reservas = cursor.fetchall()

        return {'status': 'success', 'mesas': [
            {'usuario_id': r[0], 'cliente': r[1], 'personas': r[2]} for r in reservas
        ]}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()


# Cancelar una reserva
def cancelar_reserva(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        usuario_id = content['usuario_id']

        # Verificar si existe una reserva activa
        cursor.execute("""
        SELECT id, fonda_id
        FROM reservas
        WHERE usuario_id = ? AND estado = 'pendiente'
        """, (usuario_id,))
        reserva = cursor.fetchone()

        if not reserva:
            return {'status': 'failure', 'message': 'No tienes una reserva activa para cancelar.'}

        # Liberar las mesas ocupadas
        reserva_id, fonda_id = reserva
        cursor.execute("""
        UPDATE mesas
        SET estado = 'disponible'
        WHERE fonda_id = ? AND estado = 'ocupada'
        """, (fonda_id,))

        # Cambiar el estado de la reserva
        cursor.execute("""
        UPDATE reservas
        SET estado = 'cancelada'
        WHERE id = ?
        """, (reserva_id,))

        # Cambiar el estado del usuario a 'libre'
        cursor.execute("""
        UPDATE usuarios
        SET estado_reserva = 'libre'
        WHERE id = ?
        """, (usuario_id,))

        conn.commit()
        return {'status': 'success', 'message': 'Reserva cancelada exitosamente.'}
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
        if action == 'reserve':
            response_content = reservar_mesa(request.content)
        elif action == 'view_reservations':
            response_content = listar_reservas_pendientes(request.content)
        elif action == 'release_table':
            response_content = liberar_mesa(request.content)
        elif action == 'cancel_reservation':
            response_content = cancelar_reserva(request.content)
        elif action == 'check_reservation_status':
            response_content = check_reservation_status(request.content)
        else:
            response_content = {'status': 'failure', 'message': 'Acción no válida'}

        print("Respuesta a enviar:", response_content)  # Depuración
        response = service.Response(s.name, response_content)
        s.send(response)
    s.close()

if __name__ == "__main__":
    s = service.Service('mesas')  # Nombre del servicio
    run_service(s)
