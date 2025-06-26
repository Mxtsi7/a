import sqlite3
from typing import List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Alimento:
    """Modelo de datos para Alimento"""
    nombre: str
    calorias_100gr: Optional[float] = None
    calorias_porcion: Optional[float] = None
    id: Optional[int] = None

class AlimentoRepositoryInterface(ABC):
    """Interface para el repositorio de alimentos"""
    
    @abstractmethod
    def existe_alimento(self, nombre: str) -> bool:
        pass
    
    @abstractmethod
    def buscar_similares(self, nombre: str) -> List[str]:
        pass
    
    @abstractmethod
    def guardar_alimento(self, alimento: Alimento) -> bool:
        pass
    
    @abstractmethod
    def obtener_alimento_por_nombre(self, nombre: str) -> Optional[Alimento]:
        pass

class SqliteAlimentoRepository(AlimentoRepositoryInterface):
    """Implementación concreta del repositorio usando SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = None
        self._cursor = None
        self._conectar()
    
    def _conectar(self):
        """Establece conexión con la base de datos"""
        try:
            self._conn = sqlite3.connect(self.db_path)
            self._cursor = self._conn.cursor()
        except sqlite3.Error as e:
            raise Exception(f"Error al conectar con la base de datos: {e}")
    
    def existe_alimento(self, nombre: str) -> bool:
        """Verifica si un alimento ya existe en la base de datos"""
        nombre_normalizado = nombre.strip().lower()
        
        try:
            self._cursor.execute(
                "SELECT COUNT(*) FROM alimento WHERE LOWER(nombre) = ?", 
                (nombre_normalizado,)
            )
            resultado = self._cursor.fetchone()
            return resultado[0] > 0
        except sqlite3.Error:
            return False
    
    def buscar_similares(self, nombre: str) -> List[str]:
        """Busca alimentos con nombres similares"""
        nombre_normalizado = nombre.strip().lower()
        
        try:
            self._cursor.execute(
                "SELECT nombre FROM alimento WHERE LOWER(nombre) LIKE ? AND LOWER(nombre) != ?", 
                (f"%{nombre_normalizado}%", nombre_normalizado)
            )
            resultados = self._cursor.fetchall()
            return [r[0] for r in resultados]
        except sqlite3.Error:
            return []
    
    def guardar_alimento(self, alimento: Alimento) -> bool:
        """Guarda un alimento en la base de datos"""
        try:
            self._cursor.execute(
                "INSERT INTO alimento (nombre, calorias_100gr, calorias_porcion) VALUES (?, ?, ?)",
                (alimento.nombre, alimento.calorias_100gr, alimento.calorias_porcion)
            )
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al guardar alimento: {e}")
            return False
    
    def obtener_alimento_por_nombre(self, nombre: str) -> Optional[Alimento]:
        """Obtiene un alimento por su nombre"""
        try:
            self._cursor.execute(
                "SELECT id, nombre, calorias_100gr, calorias_porcion FROM alimento WHERE LOWER(nombre) = ?",
                (nombre.lower(),)
            )
            resultado = self._cursor.fetchone()
            
            if resultado:
                return Alimento(
                    id=resultado[0],
                    nombre=resultado[1],
                    calorias_100gr=resultado[2],
                    calorias_porcion=resultado[3]
                )
            return None
        except sqlite3.Error:
            return None
    
    def cerrar_conexion(self):
        """Cierra la conexión con la base de datos"""
        try:
            if self._conn:
                self._conn.close()
        except sqlite3.Error as e:
            print(f"Error al cerrar la conexión: {e}")
    
    def __del__(self):
        """Destructor para cerrar la conexión automáticamente"""
        self.cerrar_conexion()