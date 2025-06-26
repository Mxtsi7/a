from model.util.base import DBManager
from .mensajes import MessageHandler  # Importamos nuestro manejador de mensajes
import os
import shutil

def obtener_datos_usuario(nombre_usuario):
    """Obtiene fecha_nacimiento, género, meta calórica, nivel de actividad, estatura y peso actual del usuario."""
    try:
        conn = DBManager.conectar_usuario(nombre_usuario)
        query_user = "SELECT fecha_nacimiento, genero, meta_cal, nivel_actividad, estatura FROM datos WHERE nombre = ?"
        user_data = DBManager.ejecutar_query(conn, query_user, (nombre_usuario,))

        query_peso = """
            SELECT peso, fecha 
            FROM peso 
            ORDER BY 
                SUBSTR(fecha, 7, 4) DESC, -- Año (YYYY)
                SUBSTR(fecha, 4, 2) DESC, -- Mes (MM)
                SUBSTR(fecha, 1, 2) DESC  -- Día (DD)
            LIMIT 1
        """
        peso_data = DBManager.ejecutar_query(conn, query_peso)

        DBManager.cerrar_conexion(conn)

        if user_data and peso_data:
            fecha_nacimiento, genero, meta_cal, nivel_actividad, estatura = user_data
            peso, fecha = peso_data
            return fecha_nacimiento, genero, peso, nivel_actividad, meta_cal, estatura
        else:
            return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
    except Exception as e:
        # Usamos nuestro MessageHandler en lugar de CTkMessagebox
        MessageHandler.mostrar_advertencia("Error", f"Error al acceder a la base de datos: {e}")
        return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"

def guardar_peso(nombre_usuario, nuevo_peso):
    """Guarda un nuevo peso para el usuario con la fecha actual en formato DD-MM-YYYY."""
    try:
        conn = DBManager.conectar_usuario(nombre_usuario)
        query = "INSERT INTO peso (peso, fecha) VALUES (?, strftime('%d-%m-%Y', 'now'))"
        DBManager.ejecutar_query(conn, query, (nuevo_peso,), commit=True)
        DBManager.cerrar_conexion(conn)
        return True
    except Exception as e:
        MessageHandler.mostrar_advertencia("Error", f"Error al guardar peso: {e}")
        return False

def actualizar_datos_usuario(nombre_usuario, nueva_estatura, nueva_meta_cal, nuevo_nivel_act):
    """Actualiza estatura, objetivo de calorías y nivel de actividad del usuario."""
    try:
        conexion = DBManager.conectar_usuario(nombre_usuario)
        query = """
            UPDATE datos
            SET estatura = ?, meta_cal = ?, nivel_actividad = ?
            WHERE nombre = ?
        """
        DBManager.ejecutar_query(conexion, query, (nueva_estatura, nueva_meta_cal, nuevo_nivel_act, nombre_usuario), commit=True)
        DBManager.cerrar_conexion(conexion)
        return True
    except Exception as e:
        MessageHandler.mostrar_advertencia("Error", f"Error al guardar datos: {e}")
        return False

def actualizar_contrasena(nombre_usuario, contra_actual, nueva_contra):
    """Verifica y actualiza la contraseña de un usuario."""
    try:
        conexion = DBManager.conectar_principal()
        query_verificar = "SELECT contra FROM users WHERE nombre = ?"
        resultado = DBManager.ejecutar_query(conexion, query_verificar, (nombre_usuario,))
        
        if resultado and resultado[0] == contra_actual:
            query_actualizar = "UPDATE users SET contra = ? WHERE nombre = ?"
            DBManager.ejecutar_query(conexion, query_actualizar, (nueva_contra, nombre_usuario), commit=True)
            DBManager.cerrar_conexion(conexion)
            return True
        else:
            DBManager.cerrar_conexion(conexion)
            return False
    except Exception as e:
        MessageHandler.mostrar_advertencia("Error", f"Error al actualizar contraseña: {e}")
        return False

def obtener_configuracion_recordatorio(nombre_usuario):
    """Obtiene el estado y frecuencia del recordatorio de peso."""
    try:
        conn = DBManager.conectar_usuario(nombre_usuario)
        query = "SELECT recordatorio, cantidad_dias FROM datos WHERE nombre = ?"
        config = DBManager.ejecutar_query(conn, query, (nombre_usuario,))
        DBManager.cerrar_conexion(conn)
        return config if config else ("off", "1 día")
    except Exception as e:
        MessageHandler.mostrar_advertencia("Error", f"Error al cargar configuración: {e}")
        return "off", "1 día"

def guardar_configuracion_recordatorio(nombre_usuario, estado, frecuencia):
    """Guarda la configuración del recordatorio del usuario."""
    try:
        conn = DBManager.conectar_usuario(nombre_usuario)
        query = """
            UPDATE datos 
            SET recordatorio = ?, cantidad_dias = ? 
            WHERE nombre = ?
        """
        DBManager.ejecutar_query(conn, query, (estado, frecuencia, nombre_usuario), commit=True)
        DBManager.cerrar_conexion(conn)
        return True
    except Exception as e:
        MessageHandler.mostrar_advertencia("Error", f"Error al guardar configuración: {e}")
        return False

def eliminar_usuario(nombre_usuario, contraseña):
    """Elimina la cuenta del usuario si la contraseña es correcta."""
    try:
        conexion = DBManager.conectar_principal()
        query_verificar = "SELECT contra FROM users WHERE nombre = ?"
        resultado = DBManager.ejecutar_query(conexion, query_verificar, (nombre_usuario,))

        if resultado and resultado[0] == contraseña:
            usuario_path = f'./users/{nombre_usuario}'
            if os.path.exists(usuario_path):
                shutil.rmtree(usuario_path)

            DBManager.ejecutar_query(conexion, "DELETE FROM users WHERE nombre = ?", (nombre_usuario,), commit=True)
            DBManager.cerrar_conexion(conexion)
            return True
        else:
            DBManager.cerrar_conexion(conexion)
            return False
    except Exception as e:
        MessageHandler.mostrar_advertencia("Error", f"Error al eliminar cuenta: {e}")
        return False