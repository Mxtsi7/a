import requests
from datetime import datetime
from .repositorio_abs import AlimentoRepository
from PyQt6.QtWidgets import QMessageBox
from typing import List

class ApiAlimentoRepository(AlimentoRepository):
    """
    Implementación del repositorio que se comunica con la API FastAPI
    en lugar de la base de datos SQLite local.
    """
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        # Verificar si la API está en línea al iniciar
        try:
            response = requests.get(f"{self.base_url}/", timeout=2)
            response.raise_for_status()
            print("Conexión con la API establecida con éxito.")
        except requests.RequestException as e:
            print(f"Error de conexión con la API: {e}")
            # Este mensaje es útil para que el desarrollador sepa que la API no está corriendo
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Error de Conexión")
            msg_box.setText("No se pudo conectar con el servidor de alimentos. "
                            "Por favor, asegúrese de que la API esté en ejecución.")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.exec()
            # Podríamos lanzar una excepción aquí para detener la carga de la app si se prefiere
            # raise ConnectionError("No se pudo conectar a la API.") from e


    def get_ultimo_insertado(self):
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        try:
            response = requests.get(f"{self.base_url}/resumen-diario/{fecha_hoy}")
            if response.status_code == 404:
                return "¡Agrega un alimento!"
            response.raise_for_status()
            data = response.json()
            if data.get("consumos"):
                # Ordenar por hora para obtener el último real
                consumos_ordenados = sorted(data["consumos"], key=lambda x: x['hora'], reverse=True)
                return consumos_ordenados[0]['nombre']
            return "¡Agrega un alimento!"
        except requests.RequestException:
            return "Error al conectar"


    def buscar_alimento_en_db(self, nombre_alimento):
        """Busca un alimento en la API, primero localmente y luego externamente."""
        try:
            # El payload para la consulta es correcto
            payload = {"nombre": nombre_alimento}
            response = requests.post(f"{self.base_url}/consultar-alimento", json=payload, timeout=5)
            response.raise_for_status()
            data = response.json()

            # --- ¡LÍNEA CORREGIDA! ---
            # Asegúrate de que las claves coincidan exactamente con el modelo de la API.
            return (data['nombre'], data.get('calorias_100gr'), data.get('calorias_porcion'))

        except requests.RequestException as e:
            # Es buena idea hacer el error más descriptivo
            raise Exception(f"No se pudo conectar a la API para buscar '{nombre_alimento}'.") from e
        except KeyError as e:
            # Esto nos ayuda a depurar si falta otra clave
            raise Exception(f"La respuesta de la API no contiene la clave esperada: {e}")
        

    def cargar_alimentos(self) -> List[str]:
        """
        ¡Vuelve a la vida! Carga la lista de alimentos personalizados desde la API.
        """
        try:
            response = requests.get(f"{self.base_url}/alimentos", timeout=5)
            if response.status_code == 200:
                alimentos = response.json()
                return [alimento['nombre'] for alimento in alimentos]
            return []
        except requests.RequestException:
            print("ADVERTENCIA: No se pudo cargar la lista de alimentos desde la API.")
            return []
        
    def calcular_calorias_totales(self):
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        try:
            response = requests.get(f"{self.base_url}/resumen-diario/{fecha_hoy}")
            if response.status_code == 404:
                return 0.0
            response.raise_for_status()
            data = response.json()
            return data.get('resumen_total', {}).get('calorias', 0.0)
        except requests.RequestException:
            return 0.0
        
    def insert_alimento(self, nombre, fecha, hora, cantidad, calorias):
        """
        Inserta el alimento consumido usando la nueva API simplificada.
        El 'calorias' que recibe ya es el total calculado por la UI.
        """
        try:
            # La fecha viene en 'dd-mm-YYYY', la convertimos a objeto 'date'
            fecha_obj = datetime.strptime(fecha, '%d-%m-%Y').date()

            # Construir el payload para el nuevo endpoint
            consumo_data = {
                "nombre": nombre,
                "fecha": fecha_obj.isoformat(), # Convertir a string YYYY-MM-DD
                "hora": hora,
                "cantidad": float(cantidad),
                "total_cal": float(calorias)
            }
            
            # El cuerpo de la petición ahora es {"consumo": {...}}
            payload = {"consumo": consumo_data}

            # Apuntar al nuevo endpoint /registrar-consumo
            response = requests.post(f"{self.base_url}/registrar-consumo", json=payload)
            response.raise_for_status()

        except requests.RequestException as e:
            error_msg = f"Error de API: {e}"
            if e.response:
                error_msg += f"\nDetalle: {e.response.text}"
            raise Exception(error_msg)
        
        except Exception as e:
            # Capturar otros errores como el de formato de fecha
            raise Exception(f"Error al preparar los datos para la API: {e}")



    def actualizar_calorias_totales(self):
        """
        Esta función no es necesaria cuando se usa la API, ya que la UI
        vuelve a llamar a `calcular_calorias_totales` para refrescar el valor.
        """
        pass