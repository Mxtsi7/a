class PulseSettings:
    """Clase para configuración de la medición de pulso"""
    
    def __init__(self):
        """Inicializa la configuración con valores predeterminados"""
        self.total_clicks = 10       # Número total de clicks a registrar
        self.timeout = 2.0           # Tiempo en segundos para resetear las pulsaciones
        self.max_stored_clicks = 4   # Máximo número de clicks almacenados para cálculos