import sqlite3

def agregar_administrador():
    conn = sqlite3.connect("fondas.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO usuarios (nombre, apellido, username, contraseña, rol)
        VALUES (?, ?, ?, ?, 'admin')
        """, ("Admin", "Principal", "admin", "admin123"))
        conn.commit()
        print("Administrador agregado con éxito.")
    except sqlite3.IntegrityError:
        print("El administrador ya existe.")
    finally:
        conn.close()

if __name__ == "__main__":
    agregar_administrador()

