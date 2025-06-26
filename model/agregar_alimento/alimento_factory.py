from abc import ABC, abstractmethod
from .repositorio_alimentos import SqliteAlimentoRepository
from .servicio_alimentos import AlimentoService, PyQt6NotificationService
from .repositorio_api import ApiAlimentoRepository

# Interfaz para la fábrica
class AlimentoFactory(ABC):
    @abstractmethod
    def crear_alimento_service(self, usuario: str) -> AlimentoService:
        pass

    @abstractmethod
    def crear_notification_service(self, parent=None) -> PyQt6NotificationService:
        pass

# Fábrica concreta para SQLite
class SqliteAlimentoFactory(AlimentoFactory):
    def crear_alimento_service(self, usuario: str) -> AlimentoService:
        db_path = f"./users/{usuario}/alimentos.db"
        repository = SqliteAlimentoRepository(db_path)
        return AlimentoService(repository)

    def crear_notification_service(self, parent=None) -> PyQt6NotificationService:
        return PyQt6NotificationService(parent)
    
class ApiAlimentoFactory(AlimentoFactory):
    """Fábrica concreta para crear servicios que usan la API."""
    def crear_alimento_service(self, usuario: str) -> AlimentoService:
        # El 'usuario' ya no es necesario, pero mantenemos la firma del método
        repository = ApiAlimentoRepository() # Usamos el nuevo repositorio
        return AlimentoService(repository)

    def crear_notification_service(self, parent=None) -> PyQt6NotificationService:
        return PyQt6NotificationService(parent)