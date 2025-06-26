from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMessageBox, QTextEdit,
                             QScrollArea, QComboBox, QDialog, QLineEdit,
                             QCheckBox, QProgressBar)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject
from .GerminiAssitant import GeminiAssistant


class MessageWorker(QObject):
    finished = pyqtSignal(str, object)
    
    def __init__(self, assistant, message):
        super().__init__()
        self.assistant = assistant
        self.message = message
    
    def process_message(self):
        try:
            response, food_info = self.assistant.send_message_with_history(self.message)
            self.finished.emit(response, food_info)
        except Exception as e:
            self.finished.emit(f"Error al procesar tu mensaje: {str(e)}", None)


class ConnectionWorker(QObject):
    finished = pyqtSignal(bool, str)
    
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
    
    def test_connection(self):
        try:
            connected, message = self.assistant.test_connection()
            self.finished.emit(connected, message)
        except Exception as e:
            self.finished.emit(False, str(e))


class APIKeySetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 Configuración de API Key")
        self.setModal(True)
        self.setFixedSize(450, 300)
        
        self.api_key = None
        self.use_password = False
        self.master_password = None
        
        self.init_ui()
        self.setStyleSheet("""
            QDialog { background-color: #2C3E50; }
            QLabel { color: white; }
            QLineEdit { 
                background-color: white; 
                border: 2px solid #BDC3C7; 
                border-radius: 8px; 
                padding: 8px; 
                font-size: 14px; 
            }
            QLineEdit:focus { border: 2px solid #3498DB; }
            QPushButton {
                background-color: #27AE60; 
                color: white; 
                border: none;
                border-radius: 8px; 
                padding: 10px; 
                font-size: 14px; 
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2ECC71; }
            QPushButton:pressed { background-color: #229954; }
            QCheckBox { color: white; font-size: 12px; }
            QCheckBox::indicator { width: 18px; height: 18px; }
        """)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("🔐 Configuración Segura de API Key")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Descripción
        desc = QLabel("Tu API key será encriptada y almacenada de forma segura.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("font-size: 12px; color: #BDC3C7; margin-bottom: 15px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Campo API Key
        api_label = QLabel("🔑 API Key de Gemini:")
        api_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(api_label)
        
        self.api_entry = QLineEdit()
        self.api_entry.setPlaceholderText("Ingresa tu API key de Google Gemini")
        self.api_entry.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.api_entry)
        
        # Checkbox para contraseña maestra
        self.password_checkbox = QCheckBox("🔒 Usar contraseña maestra personalizada (opcional)")
        self.password_checkbox.toggled.connect(self.toggle_password_field)
        layout.addWidget(self.password_checkbox)
        
        # Campo contraseña maestra (inicialmente oculto)
        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("Contraseña maestra (opcional)")
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_entry.hide()
        layout.addWidget(self.password_entry)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("💾 Guardar")
        self.save_button.clicked.connect(self.save_configuration)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("❌ Cancelar")
        self.cancel_button.setStyleSheet("background-color: #E74C3C;")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def toggle_password_field(self, checked):
        if checked:
            self.password_entry.show()
        else:
            self.password_entry.hide()
    
    def save_configuration(self):
        api_key = self.api_entry.text().strip()
        if not api_key:
            QMessageBox.warning(self, "⚠️ Advertencia", "Por favor ingresa tu API key")
            return
        
        self.api_key = api_key
        self.use_password = self.password_checkbox.isChecked()
        self.master_password = self.password_entry.text().strip() if self.use_password else None
        
        self.accept()

class GeminiChatWindow(QWidget):
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.assistant = GeminiAssistant(usuario)
        self.add_food_frame = None
        self.typing_indicator = None
        
        self.placeholder_text = "Escribe tu pregunta sobre salud, nutrición o tu progreso..."
        
        self.init_ui()
        self.setup_styles()
        
        # Verificar configuración de API key antes de continuar
        self.check_api_key_configuration()
        
        self.show_connection_status()
        self.initialize_chat()
        
        self.raise_()
        self.activateWindow()
        
    def check_api_key_configuration(self):
        """Verifica y solicita configuración de API key si es necesario"""
        try:
            status = self.assistant.get_api_key_status()
            
            if status == "not_configured":
                # Mostrar diálogo de configuración
                self.show_api_key_setup_dialog()
            elif status == "configured_but_error":
                # Hay configuración pero error al cargar
                reply = QMessageBox.question(
                    self, 
                    "⚠️ Error de API Key",
                    "Hay una configuración de API key pero no se pudo cargar.\n¿Deseas reconfigurarla?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.show_api_key_setup_dialog()
            elif status == "using_environment":
                # Usando variable de entorno - mostrar información
                self.status_label.setText("📁 Usando API key de variable de entorno")
                self.status_label.setStyleSheet("color: #F39C12; font-size: 12px;")
            elif status == "configured_and_loaded":
                # Todo correcto
                self.status_label.setText("🔐 API key configurada de forma segura")
                self.status_label.setStyleSheet("color: #2ECC71; font-size: 12px;")
            
        except Exception as e:
            print(f"Error verificando configuración de API key: {e}")
            QMessageBox.critical(self, "❌ Error", f"Error verificando configuración: {str(e)}")

    def show_api_key_setup_dialog(self):
        """Muestra el diálogo de configuración de API key"""
        try:
            dialog = APIKeySetupDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Configurar API key con los datos del diálogo
                self.setup_api_key_with_dialog_data(dialog)
            else:
                # Usuario canceló - mostrar mensaje
                QMessageBox.information(
                    self, 
                    "ℹ️ Información",
                    "Sin API key configurada, el asistente no podrá funcionar.\nPuedes configurarla más tarde desde el menú."
                )
        except Exception as e:
            print(f"Error mostrando diálogo de configuración: {e}")
            QMessageBox.critical(self, "❌ Error", f"Error en configuración: {str(e)}")

    def setup_api_key_with_dialog_data(self, dialog):
        """Configura la API key usando los datos del diálogo"""
        try:
            # Mostrar barra de progreso
            progress = QProgressBar()
            progress.setRange(0, 0)  # Indeterminado
            progress.setStyleSheet("QProgressBar { border: 2px solid #BDC3C7; border-radius: 5px; }")
            
            # Configurar API key
            success, message = self.assistant.setup_secure_api_key(
                api_key=dialog.api_key,
                use_master_password=dialog.use_password,
                master_password=dialog.master_password
            )
            
            if success:
                QMessageBox.information(self, "✅ Éxito", "API key configurada correctamente")
                self.status_label.setText("🔐 API key configurada de forma segura")
                self.status_label.setStyleSheet("color: #2ECC71; font-size: 12px;")
                # Reconectar
                self.show_connection_status()
            else:
                QMessageBox.critical(self, "❌ Error", f"Error configurando API key:\n{message}")
                
        except Exception as e:
            print(f"Error configurando API key: {e}")
            QMessageBox.critical(self, "❌ Error", f"Error en configuración: {str(e)}")


    def init_ui(self):
        self.setWindowTitle("Asistente de Salud IA")
        self.setGeometry(100, 100, 800, 600)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(80)
        self.header_frame.setStyleSheet("background-color: #34495E; border-radius: 10px;")
        main_layout.addWidget(self.header_frame)
        
        header_layout = QVBoxLayout(self.header_frame)
        self.title_label = QLabel("🤖 Asistente de Salud IA")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(self.title_label)
        config_button_layout = QHBoxLayout()
        config_button_layout.addStretch()
        
        self.config_button = QPushButton("⚙️")
        self.config_button.setFixedSize(30, 30)
        self.config_button.setToolTip("Configuración de API Key")
        self.config_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB; 
                color: white; 
                border: none;
                border-radius: 15px; 
                font-size: 12px;
            }
            QPushButton:hover { background-color: #2980B9; }
        """)
        self.config_button.clicked.connect(self.show_api_key_setup_dialog)
        config_button_layout.addWidget(self.config_button)
        
        header_layout.addLayout(config_button_layout)

        
        self.status_label = QLabel("🔄 Conectando con Gemini...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: white; font-size: 12px;")
        header_layout.addWidget(self.status_label)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #2c3e50; border: none; border-radius: 10px;") # Fondo de chat oscuro
        main_layout.addWidget(self.scroll_area)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.addStretch()
        
        self.scroll_area.setWidget(self.chat_widget)
        
        self.add_food_frame = QFrame()
        self.add_food_frame.setStyleSheet("background-color: #34495E; border-radius: 10px; padding: 10px;")
        self.add_food_frame.hide()
        main_layout.addWidget(self.add_food_frame)
        
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        input_layout.setSpacing(10)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.message_entry = QTextEdit()
        self.message_entry.setFixedHeight(80)
        self.message_entry.setPlaceholderText(self.placeholder_text)
        self.message_entry.setStyleSheet("""
            QTextEdit {
                background-color: white; color: #34495E;
                border: 2px solid #BDC3C7; border-radius: 10px;
                padding: 10px; font-size: 14px;
            }
            QTextEdit:focus { border: 2px solid #3498DB; }
        """)
        input_layout.addWidget(self.message_entry)
        
        button_layout = QVBoxLayout()
        self.send_button = QPushButton("Enviar")
        self.send_button.setFixedSize(100, 40)
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)
        
        self.clear_button = QPushButton("Limpiar")
        self.clear_button.setFixedSize(100, 35)
        self.clear_button.clicked.connect(self.clear_chat)
        button_layout.addWidget(self.clear_button)
        
        input_layout.addLayout(button_layout)
        main_layout.addWidget(input_frame)
        
        self.message_entry.installEventFilter(self)

    def add_message(self, message, sender):
        """Agrega un mensaje al chat con un layout mejorado"""
        try:
            # Layout horizontal para alinear la burbuja (izquierda o derecha)
            align_layout = QHBoxLayout()
            
            # Burbuja del mensaje (un frame con layout vertical)
            bubble_frame = QFrame()
            bubble_layout = QVBoxLayout(bubble_frame)
            bubble_frame.setMaximumWidth(int(self.width() * 0.75)) # La burbuja ocupa máx el 75% del ancho
            
            # Configuración según el remitente
            if sender == "user":
                bg_color, text_color, prefix = "#2ECC71", "#2C3E50", "Tú:"
                # Añadimos un espaciador a la izquierda para empujar la burbuja a la derecha
                align_layout.addStretch()
                align_layout.addWidget(bubble_frame)
            else: # Asistente
                bg_color, text_color, prefix = "#34495E", "white", "🤖 Asistente:"
                # Añadimos la burbuja a la izquierda y el espaciador a la derecha
                align_layout.addWidget(bubble_frame)
                align_layout.addStretch()

            # Aplicar estilo a la burbuja
            bubble_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border-radius: 12px;
                    padding: 10px;
                }}
            """)
            
            # Etiqueta del remitente ("Tú:" o "Asistente:")
            sender_label = QLabel(prefix)
            sender_label.setStyleSheet(f"color: {text_color}; font-size: 11px; font-weight: bold; background-color: transparent;")
            bubble_layout.addWidget(sender_label)
            
            # Etiqueta para el texto del mensaje (permite que el texto salte de línea)
            message_label = QLabel(message)
            message_label.setWordWrap(True)
            message_label.setOpenExternalLinks(True) # Para futuros links
            message_label.setStyleSheet(f"color: {text_color}; font-size: 13px; background-color: transparent;")
            bubble_layout.addWidget(message_label)
            
            # Contenedor principal para el mensaje, que se añade al layout del chat
            container_widget = QWidget()
            container_widget.setLayout(align_layout)
            
            # Insertar el nuevo mensaje en el chat, justo antes del espaciador final
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, container_widget)
            
            # Scroll automático hacia el final
            QTimer.singleShot(100, self.scroll_to_bottom)
            
        except Exception as e:
            print(f"Error añadiendo mensaje: {e}")
            
    def eventFilter(self, obj, event):
        if obj == self.message_entry and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)
    
    # ... Todos los demás métodos (setup_styles, show_connection_status, etc.) se mantienen igual...
    def setup_styles(self):
        button_style = """
            QPushButton {
                background-color: #27AE60; color: white; border: none;
                border-radius: 10px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2ECC71; }
            QPushButton:pressed { background-color: #229954; }
            QPushButton:disabled { background-color: #95A5A6; }
        """
        self.send_button.setStyleSheet(button_style)
        
        clear_style = """
            QPushButton {
                background-color: #E74C3C; color: white; border: none;
                border-radius: 10px; font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { background-color: #C0392B; }
        """
        self.clear_button.setStyleSheet(clear_style)
    
    def show_connection_status(self):
        self.connection_thread = QThread()
        self.connection_worker = ConnectionWorker(self.assistant)
        self.connection_worker.moveToThread(self.connection_thread)
        self.connection_thread.started.connect(self.connection_worker.test_connection)
        self.connection_worker.finished.connect(self.update_connection_status)
        self.connection_worker.finished.connect(self.connection_thread.quit)
        self.connection_thread.finished.connect(self.connection_thread.deleteLater)
        self.connection_thread.start()
    
    def update_connection_status(self, connected, message):
        try:
            if connected:
                self.status_label.setText("✅ Conectado con Gemini - Listo para ayudarte")
                self.status_label.setStyleSheet("color: #2ECC71; font-size: 12px;")
            else:
                self.status_label.setText("❌ Error de conexión - Verifica tu API Key o Internet")
                self.status_label.setStyleSheet("color: #E74C3C; font-size: 12px;")
                print(f"Error de conexión: {message}")
        except Exception as e:
            print(f"Error actualizando estado de conexión: {e}")
    
    def initialize_chat(self):
        welcome_message = """¡Hola! Soy tu asistente de salud IA personalizado. 

Estoy aquí para ayudarte con:
• Preguntas sobre nutrición y alimentación
• Información sobre tu IMC y TMB
• Consejos de hidratación y progreso diario

¿En qué puedo ayudarte hoy?"""
        self.add_message(welcome_message, "assistant")
    
    def show_add_food_option(self, food_info):
        try:
            for widget in self.add_food_frame.findChildren(QWidget):
                widget.deleteLater()
            
            layout = QVBoxLayout(self.add_food_frame)
            layout.setContentsMargins(10, 10, 10, 10)
            
            title_label = QLabel("🍽️ ¿Quieres añadir este alimento a tu registro diario?")
            title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)
            
            info_frame = QFrame()
            info_frame.setStyleSheet("background-color: #ECF0F1; border-radius: 8px; padding: 10px;")
            info_layout = QVBoxLayout(info_frame)
            
            food_label = QLabel(f"🥗 {food_info['food_name']}")
            food_label.setStyleSheet("color: #34495E; font-size: 16px; font-weight: bold;")
            food_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info_layout.addWidget(food_label)
            
            calories_label = QLabel(f"🔥 {food_info['calories']} calorías")
            calories_label.setStyleSheet("color: #27AE60; font-size: 14px;")
            calories_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info_layout.addWidget(calories_label)
            
            layout.addWidget(info_frame)
            
            controls_frame = QFrame()
            controls_layout = QHBoxLayout(controls_frame)
            
            meal_label = QLabel("Tipo de comida:")
            meal_label.setStyleSheet("color: white; font-size: 12px;")
            controls_layout.addWidget(meal_label)
            
            self.meal_selector = QComboBox()
            self.meal_selector.addItems(["Desayuno", "Almuerzo", "Cena", "Snack"])
            self.meal_selector.setCurrentText("Snack")
            self.meal_selector.setStyleSheet("background-color: white; border: 1px solid #BDC3C7; border-radius: 5px; padding: 5px; font-size: 12px;")
            controls_layout.addWidget(self.meal_selector)
            
            controls_layout.addStretch()
            
            add_button = QPushButton("✅ Añadir")
            add_button.setFixedSize(80, 32)
            add_button.setStyleSheet("QPushButton { background-color: #27AE60; color: white; border: none; border-radius: 5px; font-size: 12px; font-weight: bold; } QPushButton:hover { background-color: #2ECC71; }")
            add_button.clicked.connect(lambda: self.add_food_to_diary(food_info))
            controls_layout.addWidget(add_button)
            
            cancel_button = QPushButton("❌ Cancelar")
            cancel_button.setFixedSize(80, 32)
            cancel_button.setStyleSheet("QPushButton { background-color: #95A5A6; color: white; border: none; border-radius: 5px; font-size: 12px; font-weight: bold; } QPushButton:hover { background-color: #7F8C8D; }")
            cancel_button.clicked.connect(self.hide_add_food_option)
            controls_layout.addWidget(cancel_button)
            
            layout.addWidget(controls_frame)
            self.add_food_frame.show()
        except Exception as e:
            print(f"Error mostrando opción de añadir alimento: {e}")
    
    def hide_add_food_option(self):
        try:
            self.add_food_frame.hide()
        except Exception as e:
            print(f"Error ocultando opción de añadir alimento: {e}")
    
    def add_food_to_diary(self, food_info):
        try:
            meal_type = self.meal_selector.currentText()
            success, message = self.assistant.add_food_to_database(food_info['food_name'], food_info['calories'], meal_type)
            if success:
                success_message = f"✅ ¡Perfecto! He añadido **{food_info['food_name']}** ({food_info['calories']} calorías) a tu {meal_type}.\n\n📊 Tu registro nutricional se ha actualizado correctamente."
                self.add_message(success_message, "assistant")
                QMessageBox.information(self, "✅ Alimento Añadido", f"{food_info['food_name']} ha sido añadido a tu {meal_type}")
            else:
                self.add_message(f"❌ {message}", "assistant")
                QMessageBox.critical(self, "❌ Error", message)
        except Exception as e:
            error_msg = f"Error al añadir alimento: {str(e)}"
            self.add_message(f"❌ {error_msg}", "assistant")
            QMessageBox.critical(self, "❌ Error", error_msg)
        finally:
            self.hide_add_food_option()
    
    def send_message(self):
        try:
            message = self.message_entry.toPlainText().strip()
            if not message or not self.assistant.is_configured():
                return
            
            self.hide_add_food_option()
            self.add_message(message, "user")
            self.message_entry.clear()
            self.send_button.setText("Pensando...")
            self.send_button.setEnabled(False)
            self.add_typing_indicator()
            
            self.message_thread = QThread()
            self.message_worker = MessageWorker(self.assistant, message)
            self.message_worker.moveToThread(self.message_thread)
            self.message_thread.started.connect(self.message_worker.process_message)
            self.message_worker.finished.connect(self.handle_message_response)
            self.message_worker.finished.connect(self.message_thread.quit)
            self.message_thread.finished.connect(self.message_thread.deleteLater)
            self.message_thread.start()
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            self.add_message(f"❌ Error enviando mensaje: {str(e)}", "assistant")
    
    def handle_message_response(self, response, food_info):
        try:
            self.remove_typing_indicator()
            self.add_message(response, "assistant")
            if food_info and food_info.get('food_name') and food_info.get('calories'):
                invalid_names = ['estas', 'esta', 'esas', 'aproximadamente', 'contiene', 'tiene', 'aporta']
                if food_info['food_name'].lower() not in invalid_names:
                    self.show_add_food_option(food_info)
            
            self.send_button.setText("Enviar")
            self.send_button.setEnabled(True)
            self.message_entry.setFocus()
        except Exception as e:
            print(f"Error en manejo de respuesta: {e}")
    
    def add_typing_indicator(self):
        try:
            self.typing_indicator = QLabel("🤖 Asistente está escribiendo...")
            self.typing_indicator.setStyleSheet("color: #FFFFFF; font-size: 12px; font-style: italic; margin-left: 10px;")
            self.typing_indicator.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.typing_indicator)
            QTimer.singleShot(100, self.scroll_to_bottom)
        except Exception as e:
            print(f"Error añadiendo indicador de escritura: {e}")
    
    def remove_typing_indicator(self):
        try:
            if self.typing_indicator:
                self.typing_indicator.deleteLater()
                self.typing_indicator = None
        except Exception as e:
            print(f"Error removiendo indicador de escritura: {e}")
    
    def clear_chat(self):
        try:
            self.hide_add_food_option()
            self.assistant.clear_history()
            while self.chat_layout.count() > 1:
                child = self.chat_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            self.add_message("Chat limpiado. ¡Empecemos una nueva conversación!", "assistant")
        except Exception as e:
            print(f"Error limpiando chat: {e}")
    
    def scroll_to_bottom(self):
        try:
            scrollbar = self.scroll_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
            print(f"Error haciendo scroll: {e}")