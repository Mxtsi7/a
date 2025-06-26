import re
from datetime import datetime

class UserValidator:
    @staticmethod
    def validar_nombre(nombre):
        """Valida el nombre de usuario."""
        if not nombre:
            return False, "Por favor ingrese un nombre."
        
        nombre_regex = r'^[\w\-. ]{1,15}$'
        if not re.match(nombre_regex, nombre):
            return False, "Su nombre de usuario es muy largo o contiene caracteres inválidos."

        if nombre.strip().isdigit():
            return False, "El nombre no puede ser solo números."
        
        if re.search(r'\s{2,}', nombre):
            return False, "No se permiten múltiples espacios consecutivos en el nombre."
        
        nombres_invalidos = ['admin', 'root', 'usuario', 'test', 'default']
        if nombre.lower() in nombres_invalidos:
            return False, "Ese nombre de usuario no está permitido."
        
        return True, "Nombre válido"
    
    @staticmethod
    def validar_contraseña(contra, nombre=None):
        """Valida la contraseña del usuario según las recomendaciones de Microsoft."""
        if not contra:
            return False, "Ingrese una contraseña."

        # Requiere al menos 12 caracteres, mayúsculas, minúsculas, números y símbolos
        contra_regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+=!])[A-Za-z\d@#$%^&+=!]{12,}$'
        if not re.match(contra_regex, contra):
            return False, (
                "La contraseña debe tener al menos 12 caracteres, incluir mayúsculas, minúsculas, "
                "números y símbolos, y no debe ser una palabra común o información personal."
            )

        # No debe contener el nombre del usuario (si se proporciona)
        if nombre and nombre.lower() in contra.lower():
            return False, "La contraseña no debe contener el nombre de usuario."

        # No permitir repeticiones sospechosas
        if re.search(r'(.)\1{2,}', contra):
            return False, "La contraseña contiene repeticiones sospechosas como 'aaa' o '111'."

        # Verificar que no sea una palabra común
        palabras_comunes = ['password', 'contraseña', '123456', 'qwerty', 'admin', 'usuario']
        if contra.lower() in palabras_comunes or re.match(r'^[a-z]+$', contra.lower()):
            return False, "La contraseña no debe ser una palabra común o un patrón simple."

        return True, "Contraseña válida"

    @staticmethod
    def validar_fecha_nacimiento(fecha_str):
        """Valida la fecha de nacimiento y calcula la edad, requiere edad mínima de 13 años y máxima de 120 años."""
        try:
            fecha_nacimiento = datetime.strptime(fecha_str, '%d-%m-%Y')
            today = datetime.now()
            edad = today.year - fecha_nacimiento.year
            if (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
                edad -= 1
            
            if edad < 13:
                return False, "Debes tener al menos 13 años para registrarte."
            if edad > 120:
                return False, "La edad no puede ser mayor a 120 años."
            
            return True, edad
        except ValueError:
            return False, "Seleccione una fecha válida."
    
    @staticmethod
    def validar_numero(valor, campo):
        """Valida que un valor sea un número y esté dentro de rangos realistas."""
        if not valor and campo != "peso":
            return False, f"Ingrese un valor para {campo}."
        
        try:
            if not valor and campo == "peso":
                return True, None
            numero = float(valor)
            if numero <= 0:
                return False, f"El {campo} debe ser mayor que cero."
            
            # Rangos realistas
            if campo == "peso" and (numero < 30 or numero > 300):
                return False, "El peso debe estar entre 30 y 300 kg."
            if campo == "altura" and (numero < 100 or numero > 250):
                return False, "La altura debe estar entre 100 y 250 cm."
            if campo == "meta de calorías" and (numero < 500 or numero > 5000):
                return False, "La meta de calorías debe estar entre 500 y 5000."
            
            return True, numero
        except ValueError:
            return False, f"Ingrese un valor numérico válido para {campo}."