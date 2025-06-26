from typing import Tuple, List
from .repositorio_alimentos import AlimentoRepositoryInterface, Alimento
from .validador_alimentos import (
    NombreAlimentoValidator, 
    CaloriasValidator, 
    CamposObligatoriosValidator
)

class AlimentoService:
    """Servicio que maneja la lógica de negocio para alimentos"""
    
    def __init__(self, repository: AlimentoRepositoryInterface):
        self.repository = repository
        self.nombre_validator = NombreAlimentoValidator()
        self.calorias_validator = CaloriasValidator()
        self.campos_validator = CamposObligatoriosValidator()
    
    def agregar_alimento(self, nombre: str, calorias_str: str, tipo_porcion: str) -> Tuple[bool, str]:
        """
        Procesa la adición de un nuevo alimento.
        
        Args:
            nombre: Nombre del alimento
            calorias_str: Calorías como string
            tipo_porcion: Tipo de porción ("Por porción" o "100gr")
        
        Returns:
            Tuple con (éxito, mensaje)
        """
        # 1. Validar campos obligatorios
        es_valido, mensaje = self.campos_validator.validate(nombre, calorias_str, tipo_porcion)
        if not es_valido:
            return False, mensaje
        
        # 2. Validar y normalizar nombre
        es_valido, resultado_nombre = self.nombre_validator.validate(nombre)
        if not es_valido:
            return False, resultado_nombre
        nombre_normalizado = resultado_nombre
        
        # 3. Validar calorías
        es_valido, resultado_calorias = self.calorias_validator.validate(calorias_str)
        if not es_valido:
            return False, resultado_calorias
        calorias = resultado_calorias
        
        # 4. Verificar duplicados
        resultado_duplicado = self._verificar_duplicados(nombre_normalizado)
        if resultado_duplicado[0] != "ok":
            return False, resultado_duplicado[1]
        
        # 5. Crear objeto alimento
        alimento = self._crear_alimento(nombre_normalizado, calorias, tipo_porcion)
        
        # 6. Guardar en repository
        if self.repository.guardar_alimento(alimento):
            return True, f"Se ha registrado '{nombre_normalizado}' correctamente."
        else:
            # --- ¡CAMBIEMOS ESTE MENSAJE CONFUSO! ---
            mensaje_final = (f"No se pudo encontrar '{nombre_normalizado}' en la base de datos externa.\n\n"
                            "Intente con un nombre más simple o en inglés (ej. 'Manzana' en lugar de 'Manzana roja grande').")
            return False, mensaje_final
    
    def verificar_similares(self, nombre: str) -> Tuple[bool, List[str]]:
        """
        Verifica si existen alimentos con nombres similares.
        
        Returns:
            Tuple con (tiene_similares, lista_similares)
        """
        nombre_valido, nombre_normalizado = self.nombre_validator.validate(nombre)
        if not nombre_valido:
            return False, []
        
        similares = self.repository.buscar_similares(nombre_normalizado)
        return len(similares) > 0, similares
    
    def _verificar_duplicados(self, nombre: str) -> Tuple[str, str]:
        """
        Verifica duplicados exactos.
        
        Returns:
            Tuple con (status, mensaje) donde status puede ser "ok", "duplicado"
        """
        if self.repository.existe_alimento(nombre):
            return "duplicado", f"'{nombre}' ya está registrado en la base de datos.\nUtilice otro nombre o edite el existente."
        
        return "ok", ""
    
    def _crear_alimento(self, nombre: str, calorias: float, tipo_porcion: str) -> Alimento:
        """Crea un objeto Alimento según el tipo de porción"""
        if tipo_porcion == "100gr":
            return Alimento(
                nombre=nombre,
                calorias_100gr=calorias,
                calorias_porcion=None
            )
        else:  # "Por porción"
            return Alimento(
                nombre=nombre,
                calorias_100gr=None,
                calorias_porcion=calorias
            )

# services/notification_service.py
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject

class NotificationServiceInterface(ABC):
    """Interface para servicios de notificación"""
    
    @abstractmethod
    def mostrar_error(self, titulo: str, mensaje: str):
        pass
    
    @abstractmethod
    def mostrar_exito(self, titulo: str, mensaje: str):
        pass
    
    @abstractmethod
    def mostrar_advertencia(self, titulo: str, mensaje: str):
        pass
    
    @abstractmethod
    def mostrar_confirmacion(self, titulo: str, mensaje: str) -> bool:
        pass

class PyQt6NotificationService(QObject):
    """Implementación de notificaciones usando QMessageBox de PyQt6"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
    
    def mostrar_error(self, titulo: str, mensaje: str):
        """Muestra un mensaje de error"""
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    
    def mostrar_exito(self, titulo: str, mensaje: str):
        """Muestra un mensaje de éxito"""
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    
    def mostrar_advertencia(self, titulo: str, mensaje: str):
        """Muestra un mensaje de advertencia"""
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    
    def mostrar_confirmacion(self, titulo: str, mensaje: str) -> bool:
        """Muestra un diálogo de confirmación y retorna True si el usuario confirma"""
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Personalizar textos de botones en español
        yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
        no_button = msg_box.button(QMessageBox.StandardButton.No)
        yes_button.setText("Sí")
        no_button.setText("No")
        
        resultado = msg_box.exec()
        return resultado == QMessageBox.StandardButton.Yes