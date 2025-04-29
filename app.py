import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- Conexión y configuración inicial de la BD ---
conn = sqlite3.connect('tareas.db', check_same_thread=False)
c = conn.cursor()

# --- Crear tabla si no existe ---
c.execute('''CREATE TABLE IF NOT EXISTS tareas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    implementador TEXT,
    fecha TEXT,
    tipo TEXT,
    descripcion TEXT,
    estado TEXT DEFAULT 'pendiente'
)''')
conn.commit()

# --- Funciones auxiliares ---
def obtener_tareas():
    return pd.read_sql("SELECT * FROM tareas", conn)

def agregar_tarea(implementador, fecha, tipo, descripcion):
    c.execute('INSERT INTO tareas (implementador, fecha, tipo, descripcion) VALUES (?, ?, ?, ?)',
              (implementador, fecha, tipo, descripcion))
    conn.commit()

def actualizar_tarea(id, implementador, fecha, tipo, descripcion, estado):
    c.execute('''UPDATE tareas SET implementador=?, fecha=?, tipo=?, descripcion=?, estado=? WHERE id=?''',
              (implementador, fecha, tipo, descripcion, estado, id))
    conn.commit()

def eliminar_tarea(id):
    c.execute('DELETE FROM tareas WHERE id=?', (id,))
    conn.commit()

# --- Interfaz Streamlit ---
st.title("📋 Panel de Tareas")

menu = ["Ver tareas", "Agregar tarea", "Editar tarea", "Eliminar tarea"]
eleccion = st.sidebar.selectbox("Menú", menu)

if eleccion == "Agregar tarea":
    st.subheader("➕ Agregar nueva tarea")
    implementador = st.text_input("Implementador")
    fecha = st.date_input("Fecha de vencimiento", value=datetime.today())
    tipo = st.selectbox("Tipo", ["BR", "HEY"])
    descripcion = st.text_area("Descripción")
    if st.button("Agregar"):
        agregar_tarea(implementador, fecha.strftime('%Y-%m-%d'), tipo, descripcion)
        st.success("Tarea agregada exitosamente")

elif eleccion == "Ver tareas":
    st.subheader("📋 Lista de tareas")
    df = obtener_tareas()
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    hoy = pd.to_datetime(datetime.today().date())

    filtro_fecha = st.date_input("Filtrar por fecha (opcional)", value=None)
    mostrar_pendientes = st.checkbox("Mostrar solo tareas pendientes", value=True)

    if filtro_fecha:
        df = df[df['fecha'] == pd.to_datetime(filtro_fecha)]
    if mostrar_pendientes:
        df = df[df['estado'] != 'completada']

    for _, fila in df.iterrows():
        color = "🟥" if fila['fecha'] and fila['fecha'].date() < hoy.date() and fila['estado'] != 'completada' else "✅"
        st.markdown(f"{color} **{fila['implementador']}** - {fila['fecha'].date() if pd.notnull(fila['fecha']) else ''} - {fila['tipo']} - {fila['descripcion']} - Estado: {fila['estado']}")

    st.download_button("📥 Exportar CSV", df.to_csv(index=False), file_name="tareas.csv")

elif eleccion == "Editar tarea":
    st.subheader("✏️ Editar tarea")
    df = obtener_tareas()
    tarea_id = st.selectbox("Selecciona tarea por ID", df['id'])
    tarea = df[df['id'] == tarea_id].iloc[0]

    implementador = st.text_input("Implementador", tarea['implementador'])
    fecha = st.date_input("Fecha", value=pd.to_datetime(tarea['fecha'], errors='coerce') or datetime.today())
    tipo = st.selectbox("Tipo", ["BR", "HEY"], index=["BR", "HEY"].index(tarea['tipo']))
    descripcion = st.text_area("Descripción", tarea['descripcion'])
    estado = st.selectbox("Estado", ["pendiente", "completada"], index=["pendiente", "completada"].index(tarea['estado']))

    if st.button("Actualizar"):
        actualizar_tarea(tarea_id, implementador, fecha.strftime('%Y-%m-%d'), tipo, descripcion, estado)
        st.success("Tarea actualizada")

elif eleccion == "Eliminar tarea":
    st.subheader("🗑️ Eliminar tarea")
    df = obtener_tareas()
    tarea_id = st.selectbox("Selecciona tarea por ID para eliminar", df['id'])
    tarea = df[df['id'] == tarea_id].iloc[0]

    st.write(f"¿Estás seguro de eliminar la tarea de {tarea['implementador']} del {tarea['fecha']}?")
    if st.button("Eliminar definitivamente"):
        eliminar_tarea(tarea_id)
        st.warning("Tarea eliminada")