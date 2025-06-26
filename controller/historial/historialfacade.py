import requests
from typing import List, Dict, Any

class HistorialFacade:
    """
    Facade que obtiene los datos del historial directamente desde la API.
    Actúa como un cliente HTTP para el backend.
    """
    def __init__(self, usuario: str, base_url: str = "http://127.0.0.1:8000"):
        # El usuario se mantiene por si en el futuro se implementa un login
        self.usuario = usuario
        self.base_url = base_url

    def obtener_registros_por_rango(self, fecha_desde: str, fecha_hasta: str) -> List[Dict[str, Any]]:
        """
        Obtiene todos los registros de consumo para un rango de fechas desde la API.

        Args:
            fecha_desde (str): Fecha de inicio en formato 'YYYY-MM-DD'.
            fecha_hasta (str): Fecha de fin en formato 'YYYY-MM-DD'.

        Returns:
            Una lista de diccionarios, donde cada diccionario es un registro de consumo.
            Devuelve una lista vacía si hay un error o no hay datos.
        """
        endpoint = f"{self.base_url}/historial"
        params = {
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=5)
            # Lanza un error para respuestas 4xx o 5xx
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error de API al obtener historial: {e}")
            # Devolvemos una lista vacía para que la interfaz no se rompa.
            return []
        except ValueError: # Ocurre si la respuesta no es un JSON válido
            print("Error: La respuesta de la API no es un JSON válido.")
            return []

    def cleanup(self):
        """No hay conexiones de base de datos que cerrar en esta versión."""
        pass