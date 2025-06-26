import re
from typing import Tuple, Union
from abc import ABC, abstractmethod

class ValidatorInterface(ABC):
    """Interface para validadores siguiendo el principio de segregación de interfaces"""
    
    @abstractmethod
    def validate(self, value: str) -> Tuple[bool, str]:
        pass

class NombreAlimentoValidator(ValidatorInterface):
    """Validador específico para nombres de alimentos"""
    
    def __init__(self):
        self.patron = re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ0-9\s\-_]+$')
        self.nombres_invalidos = {"desconocido", "n/a", "---", "ninguno"}
    
    def validate(self, nombre: str) -> Tuple[bool, str]:
        """Valida que el nombre del alimento sea válido"""
        if not nombre or len(nombre.strip()) < 2:
            return False, "El nombre del alimento debe tener al menos 2 caracteres."
        
        nombre_normalizado = self._normalizar_nombre(nombre)
        
        # Validar formato
        if not self.patron.match(nombre_normalizado):
            return False, "El nombre del alimento solo puede contener letras, números, espacios, guiones y guiones bajos."
        
        # Rechazar si es completamente numérico
        if nombre_normalizado.isdigit():
            return False, "El nombre del alimento no puede ser completamente numérico."
        
        # Rechazar nombres sospechosos
        if nombre_normalizado.lower() in self.nombres_invalidos:
            return False, "Ese nombre de alimento no es válido."
        
        # Evitar caracteres no imprimibles
        if re.search(r'[^\w\sáéíóúüñÁÉÍÓÚÑ\-_]', nombre_normalizado):
            return False, "El nombre contiene caracteres no permitidos o símbolos."
        
        return True, nombre_normalizado
    
    def _normalizar_nombre(self, nombre: str) -> str:
        """Normaliza el nombre del alimento"""
        return re.sub(r'\s+', ' ', nombre).strip()

class CaloriasValidator(ValidatorInterface):
    """Validador específico para calorías"""
    
    def __init__(self, max_calorias: float = 10000):
        self.max_calorias = max_calorias
    
    def validate(self, calorias_str: str) -> Tuple[bool, Union[str, float]]:
        """Valida que las calorías sean un número positivo"""
        if not calorias_str or not calorias_str.strip():
            return False, "El campo de calorías es obligatorio."
        
        try:
            calorias = float(calorias_str.strip())
            
            if calorias <= 0:
                return False, "Las calorías deben ser un valor positivo."
            
            if calorias > self.max_calorias:
                return False, f"El valor de calorías parece ser muy alto (máximo {self.max_calorias}). Verifique la información."
            
            return True, calorias
            
        except ValueError:
            return False, "Las calorías deben ser un valor numérico."

class CamposObligatoriosValidator:
    """Validador para campos obligatorios"""
    
    def validate(self, nombre: str, calorias: str, seleccion: str) -> Tuple[bool, str]:
        """Valida que todos los campos obligatorios estén completados"""
        if not nombre or not nombre.strip():
            return False, "El nombre del alimento es obligatorio."
        
        if not calorias or not calorias.strip():
            return False, "El campo de calorías es obligatorio."
        
        if not seleccion or seleccion not in ["Por porción", "100gr"]:
            return False, "Debe seleccionar una opción válida de porción."
        
        return True, "Campos válidos"