class PulseData:
    """Clase modelo para almacenar los datos de pulsaciones"""
    
    def __init__(self):
        """Inicializa el modelo de datos vacío"""
        self.click_times = []
    
    def add_time(self, timestamp):
        """
        Añade un tiempo de click al registro
        
        Args:
            timestamp (float): Tiempo de click en segundos
        """
        self.click_times.append(timestamp)
    
    def clear_times(self):
        """Limpia todos los tiempos registrados"""
        self.click_times.clear()
    
    @property
    def count(self):
        """
        Obtiene el número de clicks registrados
        
        Returns:
            int: Número de clicks registrados
        """
        return len(self.click_times)
    
    @property
    def first_time(self):
        """
        Obtiene el primer tiempo registrado
        
        Returns:
            float: Primer tiempo registrado o None si no hay registros
        """
        if self.click_times:
            return self.click_times[0]
        return None
    
    @property
    def last_time(self):
        """
        Obtiene el último tiempo registrado
        
        Returns:
            float: Último tiempo registrado o None si no hay registros
        """
        if self.click_times:
            return self.click_times[-1]
        return None