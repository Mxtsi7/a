import sqlite3

class Calculo:
    # Rangos de IMC y sus categorías
    RANGOS_IMC = {
        (0, 16.0): ("Delgadez severa", "riesgo_alto"),
        (16.0, 17.0): ("Delgadez moderada", "riesgo_alto"),
        (17.0, 18.5): ("Delgadez leve", "riesgo_medio"),
        (18.5, 25.0): ("Peso normal", "riesgo_bajo"),
        (25.0, 30.0): ("Sobrepeso", "riesgo_medio"),
        (30.0, 35.0): ("Obesidad grado I", "riesgo_medio"),
        (35.0, 40.0): ("Obesidad grado II", "riesgo_alto"),
        (40.0, float('inf')): ("Obesidad grado III", "riesgo_alto")
    }
    
    # Rangos de TMB por género
    RANGOS_TMB = {
        "masculino": {
            (0, 1200): ("TMB baja", "riesgo_medio"),
            (1200, 1600): ("TMB normal-baja", "riesgo_bajo"),
            (1600, 2200): ("TMB normal", "riesgo_bajo"),
            (2200, 2800): ("TMB normal-alta", "riesgo_bajo"),
            (2800, float('inf')): ("TMB alta", "riesgo_medio")
        },
        "femenino": {
            (0, 1000): ("TMB baja", "riesgo_medio"),
            (1000, 1400): ("TMB normal-baja", "riesgo_bajo"),
            (1400, 1800): ("TMB normal", "riesgo_bajo"),
            (1800, 2200): ("TMB normal-alta", "riesgo_bajo"),
            (2200, float('inf')): ("TMB alta", "riesgo_medio")
        }
    }

    @staticmethod
    def calcular_imc(usuario):
        try:
            conn = sqlite3.connect(f"./users/{usuario}/alimentos.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT estatura FROM datos")
            resultado_estatura = cursor.fetchone()
            if resultado_estatura is None:
                raise ValueError("No se encontró la estatura para el usuario")
            estatura = resultado_estatura[0] / 100  # Convertir a metros

            cursor.execute("SELECT peso FROM peso WHERE num = (SELECT MAX(num) FROM peso)")
            resultado_peso = cursor.fetchone()
            if resultado_peso is None:
                raise ValueError("No se encontró ningún registro de peso")
            peso = resultado_peso[0]

            imc = peso / (estatura ** 2)
            return imc

        except (sqlite3.Error, ValueError) as e:
            print(f"Error al calcular IMC: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def evaluar_imc(imc):
        """Evalúa el IMC y devuelve una categoría y un nivel de riesgo"""
        if imc is None:
            return ("Error al calcular IMC", "riesgo_alto")
            
        for rango, (categoria, riesgo) in Calculo.RANGOS_IMC.items():
            min_val, max_val = rango
            if min_val <= imc < max_val:
                return (categoria, riesgo)
                
        return ("Valor IMC fuera de rango", "riesgo_alto")

    @staticmethod
    def calcular_TMB(usuario):
        try:
            conn = sqlite3.connect(f"./users/{usuario}/alimentos.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT estatura, edad, genero FROM datos")
            result = cursor.fetchone()
            if result is None:
                raise ValueError("No se encontraron datos del usuario")
            estatura, edad, genero = result
            estatura = estatura  # Altura en cm

            cursor.execute("SELECT peso FROM peso WHERE num = (SELECT MAX(num) FROM peso)")
            resultado_peso = cursor.fetchone()
            if resultado_peso is None:
                raise ValueError("No se encontró ningún registro de peso")
            peso = resultado_peso[0]

            if genero.lower() in ["hombre", "masculino"]:
                tmb = 66.47 + (13.75 * peso) + (5 * estatura) - (6.76 * edad)
            elif genero.lower() in ["mujer", "femenino"]:
                tmb = 655.1 + (9.56 * peso) + (1.85 * estatura) - (4.68 * edad)
            else:
                raise ValueError("Género no válido")
            
            return tmb

        except (sqlite3.Error, ValueError) as e:
            print(f"Error al calcular TMB: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def evaluar_TMB(tmb, genero):
        """Evalúa la TMB según el género y devuelve una categoría y un nivel de riesgo"""
        if tmb is None:
            return ("Error al calcular TMB", "riesgo_alto")
            
        genero_norm = genero.lower()
        if genero_norm not in ["hombre", "masculino", "mujer", "femenino"]:
            genero_norm = "masculino"  # Valor por defecto
        
        genero_key = "masculino" if genero_norm in ["hombre", "masculino"] else "femenino"
        
        for rango, (categoria, riesgo) in Calculo.RANGOS_TMB[genero_key].items():
            min_val, max_val = rango
            if min_val <= tmb < max_val:
                return (categoria, riesgo)
                
        return ("Valor TMB fuera de rango", "riesgo_alto")
    
    @staticmethod
    def get_latest_weight(usuario):
        try:
            conn = sqlite3.connect(f"./users/{usuario}/alimentos.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT peso FROM peso ORDER BY fecha DESC LIMIT 1")
            result = cursor.fetchone()
            
            if result is None:
                raise ValueError("No se encontró ningún registro de peso")
            
            return result[0]
        except (sqlite3.Error, ValueError) as e:
            print(f"Error al obtener el peso más reciente: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_user_gender(usuario):
        """Obtiene el género del usuario desde la base de datos"""
        try:
            conn = sqlite3.connect(f"./users/{usuario}/alimentos.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT genero FROM datos")
            result = cursor.fetchone()
            
            if result is None:
                raise ValueError("No se encontró el género del usuario")
            
            return result[0]
        except (sqlite3.Error, ValueError) as e:
            print(f"Error al obtener el género del usuario: {e}")
            return "masculino"  # Valor por defecto
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def calcular_agua_recomendada(usuario):
        """Calcula la cantidad de agua recomendada en vasos según el peso y actividad física"""
        try:
            peso = Calculo.get_latest_weight(usuario)
            if peso is None:
                return 8  # Valor por defecto si no hay peso registrado
            
            # Cálculo base: 30-35 ml por kg de peso corporal
            # Convertido a vasos de 250 ml
            vasos_base = round((peso * 35) / 250)
            
            # Limitar a un mínimo de 6 y máximo de 12 vasos
            return max(6, min(12, vasos_base))
            
        except Exception as e:
            print(f"Error al calcular agua recomendada: {e}")
            return 8  # Valor por defecto en caso de error