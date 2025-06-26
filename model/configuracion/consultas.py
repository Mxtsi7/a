from model.util.base import DBManager
from .mensajes import MessageHandler  # Importamos nuestro manejador de mensajes
import os
import shutil

# def obtener_datos_usuario(nombre_usuario):
#     """
#     Función eliminada. Los datos del usuario (fecha_nacimiento, genero, meta_cal, etc.)
#     ahora deben obtenerse a través de la API central de usuarios.
#     La base de datos local 'alimentos.db' ya no almacena esta información.
#     El peso actual se puede seguir obteniendo de la tabla 'peso' si es necesario localmente,
#     o también podría ser parte de los datos del usuario de la API.
#     """
#     # El código original ha sido eliminado.
#     # Cualquier llamada a esta función debe ser refactorizada.
#     MessageHandler.mostrar_advertencia("Función obsoleta",
#                                        "obtener_datos_usuario ha sido eliminada. Utilice la API.")
#     return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"

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

# def actualizar_datos_usuario(nombre_usuario, nueva_estatura, nueva_meta_cal, nuevo_nivel_act):
#     """
#     Función eliminada. Los datos del perfil del usuario (estatura, meta_cal, nivel_actividad)
#     ahora deben actualizarse a través de la API central de usuarios.
#     La base de datos local 'alimentos.db' ya no almacena esta información en la tabla 'datos'.
#     """
#     # El código original ha sido eliminado.
#     # Cualquier llamada a esta función debe ser refactorizada para usar la API.
#     MessageHandler.mostrar_advertencia("Función obsoleta",
#                                        "actualizar_datos_usuario ha sido eliminada. Utilice la API para actualizar datos del perfil.")
#     return False # Indica fallo ya que la operación no se puede realizar localmente.

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