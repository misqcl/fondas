import service
import sqlite3

# Validar que el operador pertenece a una fonda específica
def validar_fonda(fonda_id, user_fonda_id):
    return fonda_id == user_fonda_id

# Agregar producto al inventario
def agregar_producto(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        user_fonda_id = content['user_fonda_id']  # Fonda asociada al operador
        producto = content['producto']
        cantidad = content['cantidad']
        precio = content['precio']

        # Insertar producto en el inventario
        cursor.execute("""
        INSERT INTO inventario (fonda_id, producto, cantidad, precio)
        VALUES (?, ?, ?, ?)
        """, (user_fonda_id, producto, cantidad, precio))
        conn.commit()

        return {'status': 'success', 'message': 'Producto agregado exitosamente.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

# Eliminar producto del inventario
def eliminar_producto(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        user_fonda_id = content['user_fonda_id']  # Fonda asociada al operador
        producto = content['producto']

        # Eliminar producto del inventario
        cursor.execute("""
        DELETE FROM inventario
        WHERE fonda_id = ? AND producto = ?
        """, (user_fonda_id, producto))
        conn.commit()

        if cursor.rowcount > 0:
            return {'status': 'success', 'message': 'Producto eliminado exitosamente.'}
        else:
            return {'status': 'failure', 'message': 'Producto no encontrado.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

# Actualizar producto en el inventario
# Listar productos del inventario
def ver_inventario(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        user_fonda_id = content['user_fonda_id']

        # Filtrar solo productos (excluir promociones)
        cursor.execute("""
        SELECT producto, cantidad, precio
        FROM inventario
        WHERE fonda_id = ? AND categoria = 'producto'
        """, (user_fonda_id,))
        productos = cursor.fetchall()

        if productos:
            return {
                'status': 'success',
                'productos': [{'producto': p[0], 'cantidad': p[1], 'precio': p[2]} for p in productos]
            }
        else:
            return {'status': 'success', 'productos': []}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()




# Actualizar producto con listado previo
def actualizar_producto(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        user_fonda_id = content['user_fonda_id']  # Fonda asociada al operador

        # Validar que el operador puede gestionar esta fonda
        if not validar_fonda(user_fonda_id, user_fonda_id):
            return {'status': 'failure', 'message': 'No tiene permisos para gestionar esta fonda.'}

        producto = content['producto']
        cantidad = content['cantidad']
        precio = content['precio']

        # Actualizar producto en el inventario
        cursor.execute("""
        UPDATE inventario
        SET cantidad = ?, precio = ?
        WHERE fonda_id = ? AND producto = ?
        """, (cantidad, precio, user_fonda_id, producto))
        conn.commit()

        if cursor.rowcount > 0:
            return {'status': 'success', 'message': 'Producto actualizado exitosamente.'}
        else:
            return {'status': 'failure', 'message': 'Producto no encontrado.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

# Ver productos en el inventario
def ver_mejores_promociones(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        # Obtener promociones globales ordenadas por precio ascendente
        cursor.execute("""
        SELECT i.producto, i.precio, f.nombre AS fonda
        FROM inventario i
        JOIN fondas f ON i.fonda_id = f.id
        WHERE i.categoria = 'promocion'
        ORDER BY i.precio ASC
        """)
        promociones = cursor.fetchall()

        if promociones:
            return {
                'status': 'success',
                'promociones': [
                    {'promocion': p[0], 'precio': p[1], 'fonda': p[2]} for p in promociones
                ]
            }
        else:
            return {'status': 'success', 'promociones': []}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()




# Agregar promoción al inventario
def agregar_promocion(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        user_fonda_id = content['user_fonda_id']  # Fonda asociada al operador
        promocion = content['promocion']
        cantidad = content['cantidad']
        precio = content['precio']

        # Insertar promoción en el inventario con categoría "promoción"
        cursor.execute("""
        INSERT INTO inventario (fonda_id, producto, cantidad, precio, categoria)
        VALUES (?, ?, ?, ?, 'promocion')
        """, (user_fonda_id, promocion, cantidad, precio))
        conn.commit()

        return {'status': 'success', 'message': 'Promoción agregada exitosamente.'}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()

# Ver promociones desde el inventario
def ver_promociones(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        user_fonda_id = content['user_fonda_id']  # Fonda asociada al operador

        # Obtener promociones categorizadas como "promoción"
        cursor.execute("""
        SELECT producto, cantidad, precio
        FROM inventario
        WHERE fonda_id = ? AND categoria = 'promocion'
        """, (user_fonda_id,))
        promociones = cursor.fetchall()

        if promociones:
            return {
                'status': 'success',
                'promociones': [{'promocion': p[0], 'cantidad': p[1], 'precio': p[2]} for p in promociones]
            }
        else:
            return {'status': 'success', 'promociones': []}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()
# Ver inventario completo (productos y promociones)
def ver_inventario_completo(content):
    try:
        conn = sqlite3.connect("fondas.db")
        cursor = conn.cursor()

        user_fonda_id = content['user_fonda_id']

        # Obtener productos y promociones
        cursor.execute("""
        SELECT producto, cantidad, precio, categoria
        FROM inventario
        WHERE fonda_id = ?
        """, (user_fonda_id,))
        inventario = cursor.fetchall()

        if inventario:
            return {
                'status': 'success',
                'inventario': [
                    {'producto': item[0], 'cantidad': item[1], 'precio': item[2], 'categoria': item[3]}
                    for item in inventario
                ]
            }
        else:
            return {'status': 'success', 'inventario': []}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}
    finally:
        conn.close()



def run_service(s: service.Service):
    s.sinit()  # Inicializar el servicio con el bus
    while True:
        request = s.receive()  # Recibir solicitudes del bus
        print("Solicitud recibida:", request.content)  # Depuración

        action = request.content.get('action')
        if action == 'add':
            response_content = agregar_producto(request.content)
        elif action == 'delete':
            response_content = eliminar_producto(request.content)
        elif action == 'update':
            response_content = actualizar_producto(request.content)
        elif action == 'view':
            response_content = ver_inventario(request.content)
        elif action == 'add_promotion':
            response_content = agregar_promocion(request.content)
        elif action == 'view_promotions':
            response_content = ver_promociones(request.content)
        elif action == 'view_best_promotions':
            response_content = ver_mejores_promociones(request.content)
        elif action == 'view_all':
            response_content = ver_inventario_completo(request.content)
        else:
            response_content = {'status': 'failure', 'message': 'Acción no válida'}

        print("Respuesta a enviar:", response_content)  # Depuración
        response = service.Response(s.name, response_content)
        s.send(response)
    s.close()

if __name__ == "__main__":
    s = service.Service('invnt')  # Nombre del servicio
    run_service(s)