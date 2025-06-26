from .consultas import (
    obtener_datos_usuario,
    actualizar_datos_usuario,
    actualizar_contrasena,
    obtener_configuracion_recordatorio,
    guardar_configuracion_recordatorio,
    eliminar_usuario
)

class UserService:
    def __init__(self, usuario):
        self.usuario = usuario

    def cargar_datos_usuario(self):
        return obtener_datos_usuario(self.usuario)

    def actualizar_datos(self, nuevos_datos: dict):
        """
        Desempaqueta el diccionario de datos y llama a la función de la base de datos.
        """
        # Extraemos los valores del diccionario que nos llega desde la interfaz
        estatura = nuevos_datos.get('estatura')
        meta_calorias = nuevos_datos.get('meta_cal')
        nivel_actividad = nuevos_datos.get('nivel_actividad')
        
        # Llamamos a la función que trabaja con la BD, ahora con los valores separados
        return actualizar_datos_usuario(self.usuario, estatura, meta_calorias, nivel_actividad)


    def actualizar_contrasena(self, contra_anterior, nueva_contra):
        return actualizar_contrasena(self.usuario, contra_anterior, nueva_contra)

    def cargar_configuracion_recordatorio(self):
        return obtener_configuracion_recordatorio(self.usuario)

    def guardar_configuracion_recordatorio(self, estado, frecuencia):
        return guardar_configuracion_recordatorio(self.usuario, estado, frecuencia)

    def eliminar_usuario(self, contrasena):
        return eliminar_usuario(self.usuario, contrasena)