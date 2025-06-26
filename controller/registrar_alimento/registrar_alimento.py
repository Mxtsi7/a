
from PyQt6.QtWidgets import (QWidget,QComboBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime

from model.registrar_alimento.repositorio import SQLiteAlimentoRepository
from model.registrar_alimento.searchmanager import BuscadorManager
from model.registrar_alimento.timemanager import TiempoManager
from view.registrar_alimento.ui import UIManager
from model.util.mensajes import *
from model.registrar_alimento.api_repositorio import ApiAlimentoRepository

class RegistroAlimentoPyQt6(QWidget):
    """Clase principal para el registro de alimentos"""
    consumo_diario_actualizado = pyqtSignal()

    def __init__(self, usuario="test_user", parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.setWindowTitle("Registrar Alimento")
        self.setGeometry(100, 100, 800, 600)
        
        # Estilo principal mejorado para modo oscuro
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: Arial, sans-serif;
            }
            QLabel {
                background-color: transparent;
                color: #ffffff;
            }
        """)
        
        # Inicializar repositorio
        #self.repository = SQLiteAlimentoRepository(self.usuario)
        self.repository = ApiAlimentoRepository()
        
        # Inicializar managers
        self.ui_manager = UIManager()
        self.alimento_seleccionado = False
        
        # Variables para widgets dinámicos
        self.entry = None
        self.boton_registrar = None
        self.label_calorias = None
        self.label_hora = None
        self.boton_hora_actual = None
        self.tiempo_manager = None
        self.buscador_manager = None
        
        self.setup_ui()
        self.setup_connections()
        self.update_initial_info()
    

    # --- MÉTODO NUEVO (SLOT) ---
    def refrescar_lista_alimentos(self):
        """
        Este es el SLOT que se conectará a la señal.
        Recarga la lista de alimentos en el ComboBox.
        """
        print("RECIBIENDO SEÑAL: Refrescando lista de alimentos...")
        
        try:
            # 1. Guardar la selección actual del usuario, si hay una
            texto_actual = self.combo_box.currentText()
            
            # 2. Limpiar el ComboBox completamente
            self.combo_box.clear()
            
            # 3. Añadir el item placeholder inicial
            self.combo_box.addItem("Seleccionar alimento")
            
            # 4. Cargar la lista FRESCA de alimentos desde la base de datos
            alimentos_actualizados = self.repository.cargar_alimentos()
            self.combo_box.addItems(alimentos_actualizados)
            
            # 5. Intentar restaurar la selección del usuario
            # Si el alimento que tenía seleccionado sigue existiendo, lo vuelve a poner.
            if texto_actual in alimentos_actualizados:
                self.combo_box.setCurrentText(texto_actual)

        except Exception as e:
            print(f"Error al refrescar la lista de alimentos: {e}")

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        
        # Título principal
        titulo = self.ui_manager.create_label(
            self, "Sistema de Registro de Alimentos", 50, 10, 700, 30, 20
        )
        titulo.setStyleSheet("""
            background-color: transparent;
            color: #4CAF50;
            font-weight: bold;
            font-size: 20px;
        """)
        
        # Sección de selección de alimento
        self.ui_manager.create_frame(self, 80, 35, 250, 40, "#2E86AB")
        label_seleccionar = self.ui_manager.create_label(
            self, "Seleccionar Alimento", 90, 40, 230, 30, 16
        )
        label_seleccionar.setStyleSheet("""
            background-color: transparent;
            color: white;
            font-weight: bold;
            font-size: 16px;
        """)
        
        # ComboBox para alimentos
        self.combo_box = QComboBox(self)
        self.combo_box.move(80, 85)
        self.combo_box.resize(240, 35)
        self.combo_box.addItem("Seleccionar alimento")
        self.combo_box.setStyleSheet("""
            QComboBox {
                border: 2px solid #555555;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                background-color: #3b3b3b;
                color: #ffffff;
            }
            QComboBox:hover {
                border-color: #4CAF50;
                background-color: #454545;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
                background-color: #4CAF50;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                color: white;
            }
            QComboBox QAbstractItemView {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                border-bottom: 1px solid #555555;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #4CAF50;
                color: white;
            }
        """)
        
        # Cargar alimentos
        try:
            alimentos = self.repository.cargar_alimentos()
            self.combo_box.addItems(alimentos)
        except Exception as e:
            print(f"Error cargando alimentos: {e}")
        
        # Sección de buscador
        self.ui_manager.create_frame(self, 80, 140, 250, 40, "#2E86AB")
        label_buscador = self.ui_manager.create_label(
            self, "Buscador de alimentos", 90, 145, 230, 30, 16
        )
        label_buscador.setStyleSheet("""
            background-color: transparent;
            color: white;
            font-weight: bold;
            font-size: 16px;
        """)
        
        # Entry para buscar alimentos
        self.entry_buscar = self.ui_manager.create_entry(
            self, "Buscar alimento", 80, 190, 240
        )
        # Aplicar estilos al entry de búsqueda
        self.entry_buscar.setStyleSheet("""
            QLineEdit {
                border: 2px solid #555555;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
                background-color: #3b3b3b;
                color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
                background-color: #454545;
            }
            QLineEdit:hover {
                border-color: #777777;
            }
        """)
        
        # Lista de coincidencias (inicialmente oculta)
        self.coincidencias = self.ui_manager.create_listbox(
            self, 80, 230, 240, 100
        )
        self.coincidencias.hide()
        self.coincidencias.setStyleSheet("""
            QListWidget {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 10px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555555;
            }
            QListWidget::item:hover {
                background-color: #4CAF50;
                color: white;
            }
            QListWidget::item:selected {
                background-color: #2E86AB;
                color: white;
            }
        """)
        
        # Configurar buscador manager
        self.buscador_manager = BuscadorManager(
            self, self.entry_buscar, self.coincidencias, self.repository
        )
        
        # Información del último alimento
        self.ui_manager.create_frame(self, 410, 35, 280, 40, "#F4A261")
        label_ultimo = self.ui_manager.create_label(
            self, "Último alimento registrado:", 420, 40, 260, 30, 16
        )
        label_ultimo.setStyleSheet("""
            background-color: transparent;
            color: white;
            font-weight: bold;
            font-size: 16px;
        """)
        
        self.ui_manager.create_frame(self, 410, 80, 280, 40, "#E9C46A")
        self.label_segundo_registro = self.ui_manager.create_label(
            self, "", 420, 85, 260, 30, 16
        )
        self.label_segundo_registro.setStyleSheet("""
            background-color: transparent;
            color: #2b2b2b;
            font-weight: bold;
            font-size: 16px;
        """)
        
        # Total de calorías
        self.ui_manager.create_frame(self, 410, 140, 280, 40, "#F4A261")
        label_total = self.ui_manager.create_label(
            self, "Total calorías del día:", 420, 145, 260, 30, 16
        )
        label_total.setStyleSheet("""
            background-color: transparent;
            color: white;
            font-weight: bold;
            font-size: 16px;
        """)
        
        self.ui_manager.create_frame(self, 410, 185, 280, 40, "#E9C46A")
        self.label_total_c_mostrar = self.ui_manager.create_label(
            self, "", 420, 190, 260, 30, 16
        )
        self.label_total_c_mostrar.setStyleSheet("""
            background-color: transparent;
            color: #2b2b2b;
            font-weight: bold;
            font-size: 16px;
        """)
        
        # Botón de ayuda
        self.boton_ayuda = self.ui_manager.create_button(
            self, "?", 750, 10, 30, 30, self.mostrar_advertencia
        )
        self.boton_ayuda.setStyleSheet("""
            QPushButton {
                background-color: #2E86AB;
                border: none;
                color: white;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e5f7a;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #0d3a4f;
            }
        """)
        
        # Inicializar tiempo manager (oculto inicialmente)
        self.tiempo_manager = TiempoManager(self)
        self._hide_time_components()
    
    def setup_connections(self):
        """Configura las conexiones de señales"""
        self.combo_box.currentTextChanged.connect(self.on_alimento_select)
        # El buscador ya maneja sus propias conexiones
    
    def _hide_time_components(self):
        """Oculta los componentes de tiempo"""
        if self.tiempo_manager:
            self.tiempo_manager.hour_slider.hide()
            self.tiempo_manager.minute_slider.hide()
            self.tiempo_manager.time_label.hide()
    
    def _show_time_components(self):
        """Muestra los componentes de tiempo"""
        if self.tiempo_manager:
            # Reposicionar los componentes
            self.tiempo_manager.hour_slider.move(400, 330)
            self.tiempo_manager.hour_slider.resize(150, 30)
            self.tiempo_manager.hour_slider.show()
            
            self.tiempo_manager.minute_slider.move(570, 330)
            self.tiempo_manager.minute_slider.resize(150, 30)
            self.tiempo_manager.minute_slider.show()
            
            self.tiempo_manager.time_label.move(400, 370)
            self.tiempo_manager.time_label.resize(320, 30)
            self.tiempo_manager.time_label.show()
            
            # Aplicar estilos a los componentes de tiempo
            slider_style = """
                QSlider::groove:horizontal {
                    background-color: #555555;
                    height: 8px;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background-color: #4CAF50;
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    margin: -6px 0;
                }
                QSlider::handle:horizontal:hover {
                    background-color: #45a049;
                }
            """
            
            self.tiempo_manager.hour_slider.setStyleSheet(slider_style)
            self.tiempo_manager.minute_slider.setStyleSheet(slider_style)
            
            self.tiempo_manager.time_label.setStyleSheet("""
                background-color: transparent;
                color: #4CAF50;
                font-weight: bold;
                font-size: 16px;
                text-align: center;
            """)
    
    def on_alimento_select(self, selected_alimento):
        """Maneja la selección de un alimento"""
        if selected_alimento == "Seleccionar alimento" or not selected_alimento:
            self._hide_alimento_controls()
            return
            
        self.alimento_seleccionado = True
        
        # Obtener información del alimento
        try:
            alimento_info = self.repository.buscar_alimento_en_db(selected_alimento)
            if alimento_info:
                nombre, calorias_100g, calorias_porcion = alimento_info
                self.show_alimento_controls(calorias_porcion)
            else:
                QMessageBox.warning(self, "Advertencia", 
                                   f"No se encontró información para: {selected_alimento}")
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"Error al buscar el alimento: {str(e)}")
    
    def show_alimento_controls(self, calorias_porcion):
        """Muestra los controles cuando se selecciona un alimento"""
        
        # Frame y label para cantidad
        if not hasattr(self, 'frame_cantidad'):
            self.frame_cantidad = self.ui_manager.create_frame(
                self, 80, 350, 250, 40, "#2E86AB"
            )
        
        if not self.label_calorias:
            self.label_calorias = self.ui_manager.create_label(
                self, "", 90, 355, 230, 30, 16
            )
            self.label_calorias.setStyleSheet("""
                background-color: transparent;
                color: white;
                font-weight: bold;
                font-size: 16px;
            """)
        
        if calorias_porcion is not None:
            self.label_calorias.setText("Cantidad de porciones")
        else:
            self.label_calorias.setText("Cantidad en gramos")
        
        # Entry para cantidad
        if not self.entry:
            self.entry = self.ui_manager.create_entry(
                self, "Ingrese cantidad consumida", 80, 400, 240
            )
            self.entry.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #555555;
                    border-radius: 10px;
                    padding: 8px;
                    font-size: 14px;
                    background-color: #3b3b3b;
                    color: #ffffff;
                }
                QLineEdit:focus {
                    border-color: #4CAF50;
                    background-color: #454545;
                }
                QLineEdit:hover {
                    border-color: #777777;
                }
            """)
        else:
            self.entry.move(80, 400)
            self.entry.show()
        
        # Label para hora
        if not self.label_hora:
            self.frame_hora = self.ui_manager.create_frame(
                self, 410, 250, 280, 40, "#2E86AB"
            )
            self.label_hora = self.ui_manager.create_label(
                self, "Seleccionar Hora:", 420, 255, 260, 30, 16
            )
            self.label_hora.setStyleSheet("""
                background-color: transparent;
                color: white;
                font-weight: bold;
                font-size: 16px;
            """)
        
        # Mostrar controles de tiempo
        self._show_time_components()
        
        # Botón para hora actual
        if not self.boton_hora_actual:
            self.boton_hora_actual = self.ui_manager.create_button(
                self, "Usar Hora Actual", 400, 410, 150, 35, 
                self.tiempo_manager.set_current_time
            )
            self.boton_hora_actual.setStyleSheet("""
                QPushButton {
                    background-color: #E9C46A;
                    border: none;
                    color: #2b2b2b;
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d4a933;
                    transform: scale(1.02);
                }
                QPushButton:pressed {
                    background-color: #c19622;
                }
            """)
        else:
            self.boton_hora_actual.show()
        
        # Botón registrar
        if not self.boton_registrar:
            self.boton_registrar = self.ui_manager.create_button(
                self, "Registrar Alimento", 80, 460, 240, 50, 
                self.boton_mensajes_insert
            )
            self.boton_registrar.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    border-radius: 15px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                    transform: scale(1.02);
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """)
        else:
            self.boton_registrar.show()
    
    def _hide_alimento_controls(self):
        """Oculta los controles de alimento"""
        self._hide_time_components()
        if self.boton_hora_actual:
            self.boton_hora_actual.hide()
        if self.boton_registrar:
            self.boton_registrar.hide()
        if self.entry:
            self.entry.hide()
    
    def mostrar_advertencia(self):
        """Muestra mensaje de ayuda"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Ayuda - Registrar Alimento")
        msg.setText(
            "📋 <b>Cómo usar esta aplicación:</b><br><br>"
            "1. <b>Seleccionar alimento:</b> Usa el desplegable o el buscador<br>"
            "2. <b>Ingresar cantidad:</b> Especifica cuánto consumiste<br>"
            "3. <b>Ajustar hora:</b> Usa los controles deslizantes o 'Hora Actual'<br>"
            "4. <b>Registrar:</b> Haz clic en 'Registrar Alimento'<br><br>"
            "💡 <b>Tip:</b> Primero debes agregar alimentos en la pestaña correspondiente."
        )
        msg.setIcon(QMessageBox.Icon.Information)
        # Aplicar tema oscuro al mensaje
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #45a049;
            }
        """)
        msg.exec()
    
    def mostrar_mensaje_bienvenida(self):
        """Muestra el mensaje de bienvenida desde el archivo central."""
        info = MENSAJES.get("registrar_alimento", {})
        titulo = info.get("titulo", "¡Bienvenido!")
        mensaje = info.get("mensaje_html", "Bienvenido al registro de alimentos.")

        msg = QMessageBox(self)
        msg.setWindowTitle(titulo)
        
        # --- LÍNEA CLAVE A AGREGAR ---
        # Le decimos explícitamente al QMessageBox que el texto es HTML.
        msg.setTextFormat(Qt.TextFormat.RichText)
        # --- FIN DE LA LÍNEA A AGREGAR ---
        
        msg.setText(mensaje)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            # ... (el resto del estilo se mantiene igual)
        """)
        msg.exec()
        
    def boton_mensajes_insert(self):
        """Maneja el botón de insertar alimento"""
        try:
            if not self.validar_datos():
                return
            
            self.insert_alimento()
            
            # Actualizar información
            self.update_initial_info()
            
            # Limpiar y ocultar controles
            self.limpiar_formulario()
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Éxito")
            msg.setText("¡Alimento registrado correctamente!")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMessageBox QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QMessageBox QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            msg.exec()
            
        except Exception as e:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"Error al registrar el alimento: {str(e)}")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMessageBox QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QMessageBox QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            msg.exec()
    
    def validar_datos(self):
        """Valida los datos antes de insertar"""
        # Validar alimento seleccionado
        alimento_combo = self.combo_box.currentText()
        alimento_buscar = self.entry_buscar.text().strip() if self.entry_buscar else ""
        
        if alimento_combo == "Seleccionar alimento" and not alimento_buscar:
            self._mostrar_mensaje_warning("Por favor, selecciona un alimento.")
            return False
        
        # Validar cantidad
        if not self.entry or not self.entry.text().strip():
            self._mostrar_mensaje_warning("Por favor, ingresa la cantidad consumida.")
            return False
        
        try:
            cantidad = float(self.entry.text())
            if cantidad <= 0:
                self._mostrar_mensaje_warning("La cantidad debe ser mayor a 0.")
                return False
        except ValueError:
            self._mostrar_mensaje_warning("Por favor, ingresa una cantidad válida (número).")
            return False
        
        return True
    
    def _mostrar_mensaje_warning(self, mensaje):
        """Muestra un mensaje de advertencia con estilo"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Advertencia")
        msg.setText(mensaje)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        msg.exec()
    
    def insert_alimento(self):
        """Inserta el alimento en la base de datos"""
        fecha_actual = datetime.now().strftime('%d-%m-%Y')
        
        # Determinar qué alimento usar
        alimento_combo = self.combo_box.currentText()
        alimento_buscar = self.entry_buscar.text().strip() if self.entry_buscar else ""
        
        alimento = (alimento_combo if alimento_combo != "Seleccionar alimento" 
                   else alimento_buscar)
        
        # Buscar información del alimento
        alimento_info = self.repository.buscar_alimento_en_db(alimento)
        if not alimento_info:
            raise Exception(f"No se encontró el alimento: {alimento}")
        
        nombre, calorias_100g, calorias_porcion = alimento_info
        cantidad = float(self.entry.text())
        
        # Calcular calorías totales
        if calorias_porcion is not None:
            calorias_totales = calorias_porcion * cantidad
        else:
            calorias_totales = (calorias_100g / 100) * cantidad
        
        hora_actual = self.tiempo_manager.get_time()
        
        # Insertar en la base de datos
        self.repository.insert_alimento(
            alimento, fecha_actual, hora_actual, cantidad, calorias_totales
        )
    
    def limpiar_formulario(self):
        """Limpia el formulario después de registrar"""
        self.combo_box.setCurrentText("Seleccionar alimento")
        if self.entry_buscar:
            self.entry_buscar.clear()
        if self.entry:
            self.entry.clear()
        self._hide_alimento_controls()
        self.alimento_seleccionado = False
    
    def update_initial_info(self):
        """Actualiza la información inicial"""
        try:
            # Último alimento
            ultimo_alimento = self.repository.get_ultimo_insertado()
            self.label_segundo_registro.setText(ultimo_alimento)
            
            # Total de calorías
            total_calorias = self.repository.calcular_calorias_totales()
            self.label_total_c_mostrar.setText(f"{total_calorias:.1f} kcal")
            
        except Exception as e:
            print(f"Error actualizando información: {e}")
            self.label_segundo_registro.setText("Error al cargar")
            self.label_total_c_mostrar.setText("0 kcal")