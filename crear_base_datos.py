# crear_base_datos.py
import sqlite3

# Conectar a la base de datos (se creará si no existe)
conn = sqlite3.connect('tareas.db')
c = conn.cursor()

# Crear la tabla
c.execute('''
CREATE TABLE IF NOT EXISTS tareas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    implementador TEXT,
    fecha TEXT,
    tipo TEXT,
    descripcion TEXT
)
''')

# Datos de ejemplo
datos = [
    ("Ana", "2025-04-01", "BR", "Tarea 1"),
    ("Luis", "2025-04-02", "HEY", "Tarea 2"),
    ("Ana", "2025-04-03", "BR", "Tarea 3")
]

# Insertar datos
c.executemany('INSERT INTO tareas (implementador, fecha, tipo, descripcion) VALUES (?, ?, ?, ?)', datos)

# Guardar cambios y cerrar
conn.commit()
conn.close()

print("Base de datos creada y poblada.")
