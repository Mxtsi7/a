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
    def calcular_imc(peso, estatura_cm):
        """
        Calcula el Índice de Masa Corporal (IMC).
        Peso en kg.
        Estatura en cm.
        """
        if not peso or not estatura_cm or estatura_cm == 0:
            print("Error al calcular IMC: Peso y estatura son requeridos y estatura no puede ser cero.")
            return None
        try:
            estatura_m = estatura_cm / 100  # Convertir a metros
            imc = peso / (estatura_m ** 2)
            return imc
        except (TypeError, ValueError) as e:
            print(f"Error al calcular IMC: {e}")
            return None

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
    def calcular_TMB(peso, estatura_cm, edad, genero):
        """
        Calcula la Tasa Metabólica Basal (TMB).
        Peso en kg.
        Estatura en cm.
        Edad en años.
        Genero como string ("masculino" o "femenino").
        """
        if not all([peso, estatura_cm, edad, genero]):
            print("Error al calcular TMB: Todos los parámetros son requeridos (peso, estatura, edad, genero).")
            return None
        try:
            # estatura_cm ya está en cm, no se necesita conversión adicional para la fórmula.
            if genero.lower() in ["hombre", "masculino"]:
                tmb = 66.47 + (13.75 * peso) + (5 * estatura_cm) - (6.76 * edad)
            elif genero.lower() in ["mujer", "femenino"]:
                tmb = 655.1 + (9.56 * peso) + (1.85 * estatura_cm) - (4.68 * edad)
            else:
                raise ValueError("Género no válido. Debe ser 'masculino' o 'femenino'.")
            
            return tmb
        except (TypeError, ValueError) as e:
            print(f"Error al calcular TMB: {e}")
            return None
    
    @staticmethod
    def evaluar_TMB(tmb, genero):
        """Evalúa la TMB según el género y devuelve una categoría y un nivel de riesgo"""
        if tmb is None:
            return ("Error al calcular TMB", "riesgo_alto")
            
        genero_norm = genero.lower()
        # Aseguramos que genero_key sea uno de los esperados en RANGOS_TMB
        if genero_norm in ["hombre", "masculino"]:
            genero_key = "masculino"
        elif genero_norm in ["mujer", "femenino"]:
            genero_key = "femenino"
        else:
            # Si el género no es reconocido, no se puede evaluar TMB apropiadamente.
            print(f"Advertencia: Género '{genero}' no reconocido para evaluar TMB. Usando 'masculino' como default podría ser impreciso.")
            genero_key = "masculino" # O manejar como error: return ("Género no válido para evaluación", "riesgo_alto")
        
        for rango, (categoria, riesgo) in Calculo.RANGOS_TMB[genero_key].items():
            min_val, max_val = rango
            if min_val <= tmb < max_val:
                return (categoria, riesgo)
                
        return ("Valor TMB fuera de rango", "riesgo_alto")
    
    @staticmethod
    def calcular_agua_recomendada(peso_kg):
        """
        Calcula la cantidad de agua recomendada en vasos según el peso.
        Peso en kg.
        """
        if peso_kg is None or peso_kg <= 0:
            print("Error al calcular agua recomendada: Peso es requerido y debe ser positivo.")
            return 8  # Valor por defecto si no hay peso válido
        try:
            # Cálculo base: 30-35 ml por kg de peso corporal
            # Convertido a vasos de 250 ml
            vasos_base = round((peso_kg * 35) / 250)
            
            # Limitar a un mínimo de 6 y máximo de 12 vasos
            return max(6, min(12, vasos_base))
        except Exception as e:
            print(f"Error al calcular agua recomendada: {e}")
            return 8  # Valor por defecto en caso de error