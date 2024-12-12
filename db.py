import sqlite3

def crear_base_datos():
    conn = sqlite3.connect("fondas.db")
    cursor = conn.cursor()

    # Tabla Usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        fonda_id INTEGER REFERENCES fondas(id),
        contraseña TEXT NOT NULL,
        rol TEXT CHECK (rol IN ('admin', 'operador', 'normal')) NOT NULL,
        estado_reserva TEXT CHECK (estado_reserva IN ('activo', 'libre')) DEFAULT 'libre'
    )
    """)

    # Tabla Fondas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fondas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        mesas INTEGER NOT NULL
    )
    """)

    # Tabla Inventario
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fonda_id INTEGER NOT NULL,
        producto TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        precio INTEGER NOT NULL,
        categoria TEXT DEFAULT 'producto',
        FOREIGN KEY(fonda_id) REFERENCES fondas(id)
    )
    """)

    # Tabla Promociones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS promociones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fonda_id INTEGER NOT NULL,
        promocion TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        precio INTEGER NOT NULL,
        FOREIGN KEY(fonda_id) REFERENCES fondas(id)
    )
    """)

    # Tabla Mesas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mesas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fonda_id INTEGER NOT NULL,
        numero INTEGER NOT NULL,
        estado TEXT CHECK (estado IN ('disponible', 'ocupada')) DEFAULT 'disponible',
        FOREIGN KEY(fonda_id) REFERENCES fondas(id)
    )
    """)

    # Tabla Opiniones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS opiniones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        fonda_id INTEGER NOT NULL,
        comentario TEXT NOT NULL,
        estrellas INTEGER CHECK (estrellas BETWEEN 1 AND 5),
        respuesta TEXT DEFAULT NULL,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(fonda_id) REFERENCES fondas(id)
    )
    """)

    # Tabla Ventas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fonda_id INTEGER NOT NULL,
        fecha DATE NOT NULL,
        total INTEGER NOT NULL,
        metodo_pago TEXT CHECK (metodo_pago IN ('debito', 'credito', 'efectivo')) NOT NULL,
        FOREIGN KEY(fonda_id) REFERENCES fondas(id)
    )
    """)

    # Tabla Reservas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reservas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        fonda_id INTEGER NOT NULL,
        mesa_id INTEGER REFERENCES mesas(id),
        personas INTEGER NOT NULL,
        estado TEXT CHECK (estado IN ('pendiente', 'completada', 'cancelada')) DEFAULT 'pendiente',
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(fonda_id) REFERENCES fondas(id)
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    crear_base_datos()
    print("Base de datos creada exitosamente.")
