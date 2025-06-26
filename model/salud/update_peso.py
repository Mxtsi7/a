from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime
from model.util.base import DBManager

class Peso(QDialog):
    # Señal para notificar cuando se actualiza el peso
    peso_actualizado = pyqtSignal()
    
    def __init__(self, parent=None, usuario="default_user", callback=None):
        super().__init__(parent)
        self.usuario = usuario
        self.callback = callback
        
        self.setWindowTitle('Actualizar peso')
        self.setFixedSize(400, 270)
        self.setModal(True)  # Equivalente a attributes('-topmost', True)
        
        # Configurar el diseño
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Label de peso actual
        self.peso_actual_label = QLabel(self.get_peso())
        self.peso_actual_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.peso_actual_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(self.peso_actual_label)
        
        # Espaciador
        main_layout.addSpacing(20)
        
        # Label de instrucción
        self.peso_label = QLabel("Ingrese su peso actual")
        self.peso_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.peso_label.setFont(QFont("Arial", 14))
        main_layout.addWidget(self.peso_label)
        
        # Entry para el peso
        self.peso_entry = QLineEdit()
        self.peso_entry.setPlaceholderText("Ejemplo: 70.5")
        self.peso_entry.returnPressed.connect(self.registrar_peso)  # Enter para registrar
        main_layout.addWidget(self.peso_entry)
        
        # Botón de registrar
        self.guardar_button = QPushButton("Registrar")
        self.guardar_button.clicked.connect(self.registrar_peso)
        main_layout.addWidget(self.guardar_button)
        
        # Espaciador al final
        main_layout.addStretch()
        
    def setup_styles(self):
        """Configura los estilos de los elementos"""
        # Estilo general del diálogo
        self.setStyleSheet("""
            QDialog {
                background-color: #2C3E50;
                color: white;
            }
        """)
        
        # Estilo del label de peso actual
        self.peso_actual_label.setStyleSheet("""
            QLabel {
                color: white;
                padding: 10px;
                background-color: #34495E;
                border-radius: 10px;
                margin: 10px 0px;
            }
        """)
        
        # Estilo del label de instrucción
        self.peso_label.setStyleSheet("""
            QLabel {
                color: #3498DB;
                background-color: #34495E;
                padding: 10px;
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        
        # Estilo del campo de entrada
        self.peso_entry.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: none;
                border-radius: 15px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498DB;
            }
        """)
        
        # Estilo del botón
        self.guardar_button.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: #34495E;
                border: none;
                border-radius: 15px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
    
    def validate_weight_change(self, new_weight):
        """Valida si el nuevo peso es razonable comparado con el peso anterior."""
        conn = None
        try:
            conn = DBManager.conectar_usuario(self.usuario)
            query = "SELECT peso, fecha FROM peso ORDER BY num DESC LIMIT 1"
            resultado = DBManager.ejecutar_query(conn, query)
            
            if not resultado:
                return True  # No hay peso previo, aceptar el nuevo peso
            
            previous_weight, previous_date_str = resultado
            previous_date = datetime.strptime(previous_date_str, "%d-%m-%Y")
            current_date = datetime.now()
            days_diff = (current_date - previous_date).days
            
            weight_diff = abs(new_weight - previous_weight)
            
            # Definir umbrales
            daily_threshold = 5  # ±5 kg en un día es sospechoso
            monthly_threshold = 15  # ±15 kg en un mes es sospechoso
            
            # Validar según el tiempo transcurrido
            if days_diff <= 1 and weight_diff > daily_threshold:
                reply = QMessageBox.question(
                    self,
                    "Confirmar Peso",
                    f"El peso ingresado ({new_weight} kg) difiere significativamente de tu peso anterior "
                    f"({previous_weight} kg) registrado hace {days_diff} día(s). ¿Es correcto este valor?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                return reply == QMessageBox.StandardButton.Yes
                
            elif days_diff <= 30 and weight_diff > monthly_threshold:
                reply = QMessageBox.question(
                    self,
                    "Confirmar Peso",
                    f"El peso ingresado ({new_weight} kg) indica un cambio significativo de {weight_diff} kg "
                    f"desde tu peso anterior ({previous_weight} kg) registrado hace {days_diff} día(s). "
                    f"¿Es correcto este valor?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                return reply == QMessageBox.StandardButton.Yes
            
            return True  # Cambio dentro de los umbrales
            
        except Exception as e:
            print(f"Error al validar peso: {e}")
            QMessageBox.critical(self, "Error", "No se pudo validar el peso. Intenta de nuevo.")
            return False
        finally:
            if conn:
                DBManager.cerrar_conexion(conn)

    def registrar_peso(self):
        """Registra el nuevo peso en la base de datos"""
        peso_texto = self.peso_entry.text().strip()
        
        if not peso_texto:
            QMessageBox.warning(self, "Advertencia", "Ingrese un peso.")
            return
        
        conn = None
        try:
            # Reemplazar coma por punto para admitir formatos comunes de decimales
            peso_texto = peso_texto.replace(',', '.')
            # Intentar convertir el peso a decimal
            peso = float(peso_texto)
            
            # Validar que el peso sea razonable
            if peso <= 0 or peso > 500:
                QMessageBox.warning(self, "Advertencia", "Ingrese un peso válido (entre 0 y 500 kg).")
                return
            
            # Validar cambio de peso
            if not self.validate_weight_change(peso):
                return  # Validación fallida o cancelada
            
            conn = DBManager.conectar_usuario(self.usuario)
            current_date = datetime.now().strftime('%d-%m-%Y')

            # Verificar si ya existe un peso registrado hoy
            query = "SELECT peso FROM peso WHERE fecha = ?"
            params = (current_date,)
            result = DBManager.ejecutar_query(conn, query, params)
            
            if result:
                # Ya existe un peso registrado hoy, preguntar si reemplazar
                reply = QMessageBox.question(
                    self,
                    "Peso ya registrado",
                    f"Ya registraste un peso ({result[0]} kg) hoy. ¿Deseas reemplazarlo con {peso} kg?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
                
                # Actualizar el peso existente
                query = "UPDATE peso SET peso = ? WHERE fecha = ?"
                params = (peso, current_date)
            else:
                # Insertar nuevo peso
                query = "INSERT INTO peso (fecha, peso) VALUES (?, ?)"
                params = (current_date, peso)
            
            DBManager.ejecutar_query(conn, query, params, commit=True)

            QMessageBox.information(self, "Éxito", "Peso actualizado correctamente")
            
            # Emitir señal de actualización
            self.peso_actualizado.emit()
            
            # Ejecutar callback si existe
            if self.callback:
                self.callback()
            
            self.accept()  # Cerrar diálogo con éxito
            
        except ValueError:
            QMessageBox.warning(self, "Advertencia", "Ingrese un peso válido (solo números).")
        except Exception as e:
            QMessageBox.critical(self, "Error", "Error al registrar el peso. Intenta de nuevo.")
            print(f"Error al registrar peso: {e}")
        finally:
            if conn:
                DBManager.cerrar_conexion(conn)

    def get_peso(self):
        """Obtiene el último peso registrado"""
        conn = None
        try:
            conn = DBManager.conectar_usuario(self.usuario)
            query = "SELECT peso FROM peso ORDER BY num DESC LIMIT 1;"
            resultado = DBManager.ejecutar_query(conn, query)
            
            if resultado:
                peso_str = resultado[0]
                return f'Su último peso registrado fue: {peso_str} kg'
            else:
                return 'Aún no has registrado tu peso!'
        except Exception as e:
            print(f"Error al obtener peso: {e}")
            return 'Error al cargar peso'
        finally:
            if conn:
                DBManager.cerrar_conexion(conn)
    
    def get_fecha(self):
        """Obtiene la fecha del último peso registrado"""
        conn = None
        try:
            conn = DBManager.conectar_usuario(self.usuario)
            query = "SELECT fecha FROM peso ORDER BY num DESC LIMIT 1;"
            resultado = DBManager.ejecutar_query(conn, query)
            
            if resultado:
                fecha_str = resultado[0]
                return fecha_str
            else:
                return None
        except Exception as e:
            print(f"Error al obtener fecha: {e}")
            return None
        finally:
            if conn:
                DBManager.cerrar_conexion(conn)

# Ejemplo de uso para testing
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    import os
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Aplicar tema oscuro
    app.setStyleSheet("""
        QWidget {
            background-color: #2C3E50;
            color: white;
        }
    """)
    
    # Crear estructura de carpetas de prueba si no existe
    test_user = "test_user"
    if not os.path.exists(f"./users/{test_user}"):
        os.makedirs(f"./users/{test_user}", exist_ok=True)
    
    def test_callback():
        print("Peso actualizado - callback ejecutado")
    
    dialog = Peso(usuario=test_user, callback=test_callback)
    dialog.exec()
    
    sys.exit(app.exec())