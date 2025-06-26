class PulseEvaluator:
    """Clase responsable de evaluar los resultados de las pulsaciones"""
    
    def evaluate_pulse(self, bpm):
        """
        Evalúa el BPM y devuelve un mensaje apropiado según la intensidad
        
        Args:
            bpm (int): Pulsaciones por minuto
            
        Returns:
            str: Mensaje de evaluación
        """
        if bpm < 100:
            return "Intenta aumentar la intensidad de tu entrenamiento."
        elif 100 <= bpm <= 120:
            return "Intensidad: ligera."
        elif 121 <= bpm <= 140:
            return "Intensidad: moderada."
        else:
            return "Intensidad alta."