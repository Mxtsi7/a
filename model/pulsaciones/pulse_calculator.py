import time
from .pulse_settings import PulseSettings
from .pulse_data import PulseData

class PulseCalculator:
    """Clase responsable de calcular y mantener el registro de pulsaciones"""
    
    def __init__(self):
        """Inicializa el calculador de pulso con la configuración por defecto"""
        self.settings = PulseSettings()
        self.pulse_data = PulseData()
        self.remaining_clicks = self.settings.total_clicks
    
    def record_click(self):
        """Registra un click de pulsación"""
        current_time = time.time()
        
        # Si ha pasado demasiado tiempo desde el último click, reiniciamos
        if (self.pulse_data.click_times and 
            current_time - self.pulse_data.click_times[-1] > self.settings.timeout):
            self.pulse_data.clear_times()
        
        # Añadimos el tiempo actual
        self.pulse_data.add_time(current_time)
        
        # Limitamos el tamaño de la cola de tiempos para cálculos precisos
        if len(self.pulse_data.click_times) > self.settings.max_stored_clicks:
            self.pulse_data.click_times.pop(0)
        
        # Decrementamos el contador de clicks restantes
        self.remaining_clicks -= 1
    
    def calculate_current_bpm(self):
        """Calcula los BPM actuales basados en los clicks registrados"""
        if len(self.pulse_data.click_times) <= 1:
            return None
        
        time_interval = self.pulse_data.click_times[-1] - self.pulse_data.click_times[0]
        clicks = len(self.pulse_data.click_times)
        
        if time_interval > 0:
            bpm = (clicks - 1) * 60 / time_interval
            return int(bpm)
        return None
    
    def calculate_final_bpm(self):
        """Calcula el BPM final basado en todos los clicks registrados"""
        if len(self.pulse_data.click_times) <= 1:
            return None
            
        time_interval = self.pulse_data.click_times[-1] - self.pulse_data.click_times[0]
        clicks = len(self.pulse_data.click_times)
        
        if time_interval > 0:
            bpm = (clicks - 1) * 60 / time_interval
            return int(bpm)
        return None