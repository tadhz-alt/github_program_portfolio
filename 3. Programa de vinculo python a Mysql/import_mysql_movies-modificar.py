import mysql.connector

# Variables para la corrección
nuevo_titulo = "Joy (Corregida)"
titulo_original = "Joy"

try:
    # 1. Conexión (Using your movies_db credentials and port 3307)
    conexion = mysql.connector.connect(
        host='localhost',
        port=3307,
        user='root',
        password='',
        database='movies_db'
    )

    # 2. Cursor
    cursor = conexion.cursor()

    # 3. Consulta UPDATE 
    # Actualiza el título donde el título original coincida
    sql = "UPDATE obsession_greatness SET title = %s WHERE title = %s"

    # 4. Valores
    valores = (nuevo_titulo, titulo_original)

    # 5. Ejecutar
    cursor.execute(sql, valores)

    # 6. Guardar cambios
    conexion.commit()

    # 7. Verificar filas afectadas
    print(f"✅ Se actualizaron {cursor.rowcount} registro(s).")

except mysql.connector.Error as e:
    print(f"❌ Error: {e}")

finally:
    if 'conexion' in locals() and conexion.is_connected():
        cursor.close()
        conexion.close()
        print("🔒 Conexión cerrada")