from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from .calculos import Calculo
from model.util.colores import *
import sqlite3
from datetime import datetime
import numpy as np

class VasoAnimado(QWidget):
    """Widget que dibuja y anima un vaso de agua"""
    
    def __init__(self, width=120, height=160, scale=1, parent=None):
        super().__init__(parent)
        self.base_width = width
        self.base_height = height
        self.scale = scale 
        self.width = width * scale
        self.height = height * scale
        
        self.setFixedSize(self.width, self.height)
        
        self.max_nivel = 118 * scale
        self.nivel = 0
        self.nivel_target = 0
        self.frame = 0
        self.incremento_por_pulsacion = self.max_nivel // 8

        # perfiles trapezoidales: (left_top, right_top, left_bottom, right_bottom)
        self.perfiles_agua = [
            (41, 80, 42, 79),  # vaso 1
            (40, 81, 43, 79),  # vaso 2
            (39, 82, 44, 80),  # vaso 3
            (38, 83, 44, 77),  # vaso 4
            (37, 84, 43, 78),  # vaso 5
            (36, 85, 42, 79),  # vaso 6
            (35, 86, 42, 80),  # vaso 7
            (34, 87, 42, 81),  # vaso 8
        ]
        
        # Timer para la animación
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(30)  # 30ms entre frames

    def incrementar_nivel(self):
        if self.nivel_target < self.max_nivel:
            self.nivel_target += self.incremento_por_pulsacion
            if self.nivel_target > self.max_nivel:
                self.nivel_target = self.max_nivel

    def set_nivel_directo(self, cantidad_vasos):
        self.nivel_target = min(cantidad_vasos * self.incremento_por_pulsacion, self.max_nivel)
        self.nivel = self.nivel_target

    def actualizar(self):
        if self.nivel < self.nivel_target:
            self.nivel += 3
        self.frame += 1
        self.update()  # Fuerza repintado

    def paintEvent(self, event):
        """Dibuja el vaso y el agua"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Limpiar fondo
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
        
        # Dibujar borde del vaso
        borde_color = QColor(180, 180, 180)
        painter.setPen(QPen(borde_color, 2 * self.scale))
        
        vaso_pts = [
            (30 * self.scale, 30 * self.scale),
            (90 * self.scale, 30 * self.scale),
            (80 * self.scale, 150 * self.scale),
            (40 * self.scale, 150 * self.scale),
        ]
        
        from PyQt6.QtCore import QPointF
        from PyQt6.QtGui import QPolygonF
        
        vaso_polygon = QPolygonF([QPointF(x, y) for x, y in vaso_pts])
        painter.drawPolygon(vaso_polygon)

        # Dibujar agua si hay nivel
        if self.nivel > 0:
            nivel_y = 150 * self.scale - self.nivel
            nivel_actual = max(1, min(8, round(self.nivel / self.incremento_por_pulsacion)))

            lt, rt, lb, rb = self.perfiles_agua[nivel_actual - 1]
            lt_x = int(lt * self.scale)
            rt_x = int(rt * self.scale)
            lb_x = int(lb * self.scale)
            rb_x = int(rb * self.scale)

            # Crear puntos de onda
            onda_pts = []
            onda_amplitud = 4 * self.scale
            onda_longitud = 20 * self.scale
            for x in range(lt_x, rt_x):
                y = nivel_y + np.sin((x + self.frame * 2) / onda_longitud) * onda_amplitud
                onda_pts.append(QPointF(x, y))

            # Crear polígono de agua
            agua_pts = [QPointF(lb_x, 150 * self.scale)] + onda_pts + [QPointF(rb_x, 150 * self.scale)]
            agua_polygon = QPolygonF(agua_pts)
            
            # Dibujar agua
            agua_color = QColor(0, 150, 255, 160)
            painter.setBrush(agua_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(agua_polygon)

class AguaManager(QWidget):
    """Manager principal para el control de consumo de agua adaptado a PyQt6"""
    
    # Señal para notificar cambios en el consumo de agua
    agua_actualizada = pyqtSignal(int, int)  # vasos_actuales, vasos_recomendados
    
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.max_vasos = 8
        self.vasos_recomendados = 8  # Valor predeterminado
        self.pulsaciones = 0
        
        self.init_ui()
        self.actualizar_vasos_recomendados()
        self.vasitos_mostrados()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Widget del vaso animado
        self.vaso = VasoAnimado(parent=self)
        vaso_layout = QHBoxLayout()
        vaso_layout.addStretch()
        vaso_layout.addWidget(self.vaso)
        vaso_layout.addStretch()
        main_layout.addLayout(vaso_layout)
        
        # Botones
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Botón para añadir vaso
        self.btn_añadir = QPushButton("Añadir vaso")
        self.btn_añadir.setFixedSize(130, 40)
        self.btn_añadir.clicked.connect(self.agregar_agua)
        buttons_layout.addWidget(self.btn_añadir)
        
        # Botón para eliminar vaso
        self.btn_eliminar = QPushButton("Eliminar vaso")
        self.btn_eliminar.setFixedSize(130, 40)
        self.btn_eliminar.clicked.connect(self.eliminar_agua)
        buttons_layout.addWidget(self.btn_eliminar)
        
        # Centrar botones
        buttons_container = QHBoxLayout()
        buttons_container.addStretch()
        buttons_container.addLayout(buttons_layout)
        buttons_container.addStretch()
        main_layout.addLayout(buttons_container)
        
        # Etiqueta para mostrar vasos actuales/recomendados
        self.lbl_info_vasos = QLabel("0/8 vasos")
        self.lbl_info_vasos.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.lbl_info_vasos)
        
        # Aplicar estilos
        self.setup_styles()

    def setup_styles(self):
        """Configura los estilos de los botones"""
        # Estilo para botón añadir
        añadir_style = """
            QPushButton {
                background-color: #2ECC71;
                color: #34495E;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """
        
        # Estilo para botón eliminar
        eliminar_style = """
            QPushButton {
                background-color: #E74C3C;
                color: #34495E;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            QPushButton:pressed {
                background-color: #A93226;
            }
        """
        
        # Estilo para etiqueta de información
        info_style = """
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """
        
        self.btn_añadir.setStyleSheet(añadir_style)
        self.btn_eliminar.setStyleSheet(eliminar_style)
        self.lbl_info_vasos.setStyleSheet(info_style)

    def actualizar_vasos_recomendados(self):
        """Actualiza la cantidad de vasos recomendados basándose en el peso del usuario"""
        try:
            self.vasos_recomendados = Calculo.calcular_agua_recomendada(self.usuario)
            self.max_vasos = self.vasos_recomendados
        except Exception as e:
            print(f"Error al calcular vasos recomendados: {e}")
            self.vasos_recomendados = 8  # Valor por defecto

    def agregar_agua(self):
        """Agrega un vaso de agua"""
        if self.pulsaciones >= self.max_vasos:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Límite alcanzado")
            msg_box.setText(f"Ya tomaste los {self.max_vasos} vasos de agua recomendados para hoy 🧊")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()
            return

        self.pulsaciones += 1
        self.vaso.incrementar_nivel()
        self.insertar_vasitos()
        self.actualizar_info_vasos()
        
        # Emitir señal de actualización
        self.agua_actualizada.emit(self.pulsaciones, self.vasos_recomendados)

        # Mostrar mensaje motivacional según avance
        self.mostrar_mensaje_motivacional()

    def eliminar_agua(self):
        """Elimina un vaso de agua"""
        if self.pulsaciones == 0:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Sin agua")
            msg_box.setText("No hay vasos que eliminar.")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()
            return

        # Diálogo de confirmación
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("¿Estás seguro?")
        msg_box.setText("¿Deseas eliminar un vaso de agua?")
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            self.pulsaciones -= 1
            self.vaso.set_nivel_directo(self.pulsaciones)
            self.eliminar_vasito()
            self.actualizar_info_vasos()
            
            # Emitir señal de actualización
            self.agua_actualizada.emit(self.pulsaciones, self.vasos_recomendados)

    def mostrar_mensaje_motivacional(self):
        """Muestra mensajes según el progreso de consumo de agua"""
        porcentaje = (self.pulsaciones / self.vasos_recomendados) * 100
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        
        if porcentaje == 100:
            msg_box.setWindowTitle("¡Felicidades!")
            msg_box.setText(f"¡Has alcanzado tu meta diaria de {self.vasos_recomendados} vasos de agua! 🎉\n"
                          "Excelente trabajo cuidando tu hidratación.")
        elif porcentaje == 50:
            msg_box.setWindowTitle("¡Buen progreso!")
            msg_box.setText(f"¡Vas por la mitad! Has tomado {self.pulsaciones} de {self.vasos_recomendados} vasos recomendados.\n"
                          "Sigue así para mantenerte bien hidratado.")
        elif porcentaje == 25:
            msg_box.setWindowTitle("¡Primer avance!")
            msg_box.setText("¡Buen comienzo! Recuerda que mantenerte hidratado es clave para tu salud.")
        else:
            return  # No mostrar mensaje para otros porcentajes
            
        msg_box.exec()

    def actualizar_info_vasos(self):
        """Actualiza la etiqueta con la información de vasos consumidos vs recomendados"""
        self.lbl_info_vasos.setText(f"{self.pulsaciones}/{self.vasos_recomendados} vasos")
        
        # Cambia el color según el progreso
        porcentaje = (self.pulsaciones / self.vasos_recomendados) * 100
        if porcentaje < 25:
            color = "#E74C3C"  # riesgo alto
        elif porcentaje < 75:
            color = "#F1C40F"  # riesgo medio
        else:
            color = "#2ECC71"  # riesgo bajo
            
        self.lbl_info_vasos.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }}
        """)

    def eliminar_vasito(self):
        """Elimina un vaso de la base de datos"""
        try:
            conn = sqlite3.connect(f"./users/{self.usuario}/alimentos.db")
            cursor = conn.cursor()
            fecha_actual = datetime.now().strftime("%d-%m-%Y")
            cursor.execute("SELECT cant FROM agua WHERE fecha = ?", (fecha_actual,))
            resultado = cursor.fetchone()

            if resultado and resultado[0] > 0:
                nueva_cantidad = resultado[0] - 1
                cursor.execute("UPDATE agua SET cant = ? WHERE fecha = ?", (nueva_cantidad, fecha_actual))

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Error de base de datos: {e}")

    def vasitos_mostrados(self):
        """Carga los vasos desde la base de datos y actualiza la visualización"""
        try:
            conn = sqlite3.connect(f"./users/{self.usuario}/alimentos.db")
            cursor = conn.cursor()
            fecha_actual = datetime.now().strftime("%d-%m-%Y")
            cursor.execute("SELECT cant FROM agua WHERE fecha = ?", (fecha_actual,))
            resultado = cursor.fetchone()
            cantidad_vasos = resultado[0] if resultado else 0
            conn.close()

            self.pulsaciones = cantidad_vasos
            self.vaso.set_nivel_directo(cantidad_vasos)
            self.actualizar_info_vasos()
            
            # Emitir señal inicial
            self.agua_actualizada.emit(self.pulsaciones, self.vasos_recomendados)
            
        except sqlite3.Error as e:
            print(f"Error al cargar datos de agua: {e}")

    def insertar_vasitos(self):
        """Inserta o actualiza un vaso en la base de datos"""
        try:
            conn = sqlite3.connect(f"./users/{self.usuario}/alimentos.db")
            cursor = conn.cursor()
            fecha_actual = datetime.now().strftime("%d-%m-%Y")
            cursor.execute("SELECT cant FROM agua WHERE fecha = ?", (fecha_actual,))
            resultado = cursor.fetchone()
            
            if resultado:
                nueva_cantidad = resultado[0] + 1
                cursor.execute("UPDATE agua SET cant = ? WHERE fecha = ?", (nueva_cantidad, fecha_actual))
            else:
                cursor.execute("INSERT INTO agua (fecha, cant) VALUES (?, 1)", (fecha_actual,))
            
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Error al insertar vaso: {e}")

    def get_progreso_agua(self):
        """Retorna el progreso actual del agua como porcentaje"""
        if self.vasos_recomendados == 0:
            return 0
        return min(100, (self.pulsaciones / self.vasos_recomendados) * 100)

    def get_info_agua(self):
        """Retorna información sobre el consumo de agua"""
        return {
            'vasos_actuales': self.pulsaciones,
            'vasos_recomendados': self.vasos_recomendados,
            'porcentaje': self.get_progreso_agua()
        }