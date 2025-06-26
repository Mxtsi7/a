from PyQt6.QtCore import QObject, pyqtSignal

class Subject(QObject):
    """
    Implementación del patrón Observer usando las señales de PyQt6.
    Hereda de QObject para poder emitir señales.
    """
    # Señal que se emite cuando se notifica a los observadores
    observer_notified = pyqtSignal(object)  # object permite pasar cualquier tipo de dato
    
    def __init__(self):
        super().__init__()
        self._observers = []

    def attach(self, observer):
        """Agrega un observador a la lista"""
        if observer not in self._observers:
            self._observers.append(observer)
            # Conectar la señal al método update del observador si existe
            if hasattr(observer, 'update'):
                self.observer_notified.connect(observer.update)

    def detach(self, observer):
        """Remueve un observador de la lista"""
        if observer in self._observers:
            self._observers.remove(observer)
            # Desconectar la señal del observador
            if hasattr(observer, 'update'):
                try:
                    self.observer_notified.disconnect(observer.update)
                except TypeError:
                    # La conexión no existía
                    pass

    def notify(self, message=None):
        """
        Notifica a todos los observadores.
        Puede usar tanto el método tradicional como las señales de PyQt6.
        """
        # Método tradicional (para compatibilidad)
        for observer in self._observers:
            if hasattr(observer, 'update'):
                observer.update(message)
        
        # Método usando señales de PyQt6
        self.observer_notified.emit(message)