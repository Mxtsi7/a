import requests
from typing import List, Optional
from .repositorio_alimentos import AlimentoRepositoryInterface, Alimento

class ApiAlimentoRepository(AlimentoRepositoryInterface):
    """Implementación del repositorio que habla con nuestra API FastAPI."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url

    def existe_alimento(self, nombre: str) -> bool:
        """Verifica si el alimento puede ser encontrado por la API."""
        try:
            # Usamos el endpoint que ya tenemos para ver si nos da una respuesta exitosa
            response = requests.post(f"{self.base_url}/consultar-alimento", json={"nombre": nombre}, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def guardar_alimento(self, alimento: Alimento) -> bool:
        """Ahora SÍ guarda el alimento en la base de datos de la API."""
        payload = {
            "nombre": alimento.nombre,
            "calorias_100gr": alimento.calorias_100gr,
            "calorias_porcion": alimento.calorias_porcion
        }
        try:
            # Apuntamos al nuevo endpoint para guardar
            response = requests.post(f"{self.base_url}/alimentos", json=payload, timeout=5)
            # 201 Created es el código de éxito
            return response.status_code == 201
        except requests.RequestException:
            return False

    def buscar_similares(self, nombre: str) -> List[str]:
        # La API actual no tiene un endpoint para buscar similares, devolvemos una lista vacía.
        return []

    def obtener_alimento_por_nombre(self, nombre: str) -> Optional[Alimento]:
        # Podemos simular esto llamando a la API
        if self.existe_alimento(nombre):
            response = requests.post(f"{self.base_url}/consultar-alimento", json={"nombre": nombre})
            data = response.json()
            # Creamos un objeto Alimento temporal
            return Alimento(nombre=data['nombre'], calorias_100gr=data.get('calorias_por_100g'))
        return None