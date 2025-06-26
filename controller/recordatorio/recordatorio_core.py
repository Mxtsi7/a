import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer, QObject
from model.subject import Subject
from .recordatorio_conexion import _obtener_conexion
from .recordatorio_utils import (
    _mostrar_error, _debe_mostrar_recordatorio,
    MOSTRADO_HOY, MOSTRADO, ON, OFF,
)

class Recordatorio(Subject):
    
    def __init__(self, usuario, parent=None):
        super().__init__()
        self.usuario = usuario
        self.parent = parent  # Widget padre para los mensajes

    def _activar_recordatorio(self, cursor):
        """Activa el recordatorio en la base de datos"""
        cursor.execute("""
            UPDATE datos 
            SET recordatorio = ? 
            WHERE nombre = ?
        """, (ON, self.usuario))

    def _marcar_recordatorio_mostrado(self, cursor):
        """Marca el recordatorio como mostrado hoy"""
        cursor.execute("""
            UPDATE datos 
            SET recordatorio = ?, ultimo_msj = ? 
            WHERE nombre = ?
        """, (MOSTRADO_HOY, datetime.now().date().strftime('%Y-%m-%d'), self.usuario))

    def recordar_actualizar_peso(self):
        """Verifica si debe mostrar recordatorio para actualizar peso"""
        try:
            with _obtener_conexion(self.usuario) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT recordatorio, cantidad_dias, ultimo_msj FROM datos WHERE nombre = ?", (self.usuario,))
                config = cursor.fetchone()

                if not config:
                    return

                estado, frecuencia, ultimo_msj = config
                frecuencia_dias = int(frecuencia.split()[0]) if frecuencia else 1

                cursor.execute("SELECT fecha FROM peso ORDER BY fecha DESC LIMIT 1")
                ultimo_registro = cursor.fetchone()

                if ultimo_registro and ultimo_registro[0]:
                    ultima_fecha = datetime.strptime(ultimo_registro[0], '%d-%m-%Y')
                    dias_diferencia = (datetime.now() - ultima_fecha).days
                else:
                    dias_diferencia = None

                if _debe_mostrar_recordatorio(dias_diferencia, frecuencia_dias, estado, ultimo_msj):
                    self.notify("recordatorio_peso")
                    self._marcar_recordatorio_mostrado(cursor)
                else:
                    self._activar_recordatorio(cursor)

                conn.commit()

        except sqlite3.Error as e:
            _mostrar_error(f"Error al acceder a la base de datos: {e}", self.parent)
        except Exception as e:
            _mostrar_error(f"Error inesperado: {e}", self.parent)

    def recordatorio_por_defecto(self):
        """Configura los valores por defecto del recordatorio"""
        try:
            with _obtener_conexion(self.usuario) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT cantidad_dias, ultimo_msj FROM datos WHERE nombre = ?", (self.usuario,))
                resultado = cursor.fetchone()

                if resultado:
                    cantidad_dias, ultimo_msj = resultado
                    if not cantidad_dias:
                        cursor.execute("UPDATE datos SET cantidad_dias = '1 día' WHERE nombre = ?", (self.usuario,))
                    if not ultimo_msj:
                        cursor.execute("UPDATE datos SET ultimo_msj = ? WHERE nombre = ?", (None, self.usuario))
                else:
                    cursor.execute("""
                        INSERT INTO datos (nombre, recordatorio, cantidad_dias, ultimo_msj)
                        VALUES (?, ?, '1 día', ?)
                    """, (self.usuario, OFF, None))

                conn.commit()

        except sqlite3.Error as e:
            _mostrar_error(f"Error al acceder a la base de datos: {e}", self.parent)

    def mostrar_recordatorio_añadido(self):
        """Muestra recordatorios programados para la fecha y hora actuales"""
        try:
            with _obtener_conexion(self.usuario) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Titulo, Fecha, Hora FROM recordatorios WHERE Usuario = ?", (self.usuario,))
                recordatorios = cursor.fetchall()

                presente = datetime.now()
                fecha_hoy = presente.strftime("%Y-%m-%d")
                hora_hoy = presente.strftime("%H:%M")
                
                if recordatorios:
                    for titulo, fecha, hora in recordatorios:
                        if fecha == fecha_hoy and hora == hora_hoy:
                            msg_box = QMessageBox(self.parent)
                            msg_box.setWindowTitle("Recordatorio")
                            msg_box.setText(f"Recordatorio: {titulo}")
                            msg_box.setIcon(QMessageBox.Icon.Information)
                            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                            msg_box.exec()

        except sqlite3.Error as e:
            _mostrar_error(f"Error al acceder a la base de datos: {e}", self.parent)

    def iniciar_recordatorios(self, main_widget):
        """Inicia el sistema de recordatorios con un timer que se ejecuta cada minuto"""
        self.mostrar_recordatorio_añadido()
        
        # Crear un QTimer para repetir la verificación cada 60 segundos (60000 ms)
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.iniciar_recordatorios(main_widget))
        self.timer.start(60000)  # 60 segundos en milisegundos