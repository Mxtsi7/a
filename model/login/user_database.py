import sqlite3
import os
from abc import ABC, abstractmethod

class IUserDatabase(ABC):
    @abstractmethod
    def crear_db_usuario(self, nombre_usuario):
        pass

class UserDatabase(IUserDatabase):
    def crear_db_usuario(self, nombre_usuario):
        """
        Crea la base de datos para un nuevo usuario, pero solo con las tablas
        que se gestionan localmente, ya que alimentos y consumo ahora los maneja la API.
        """
        directorio = f'./users/{nombre_usuario}'
        os.makedirs(directorio, exist_ok=True)
        
        # ¡Corregido! Mantenemos el nombre original para no romper tu código.
        db_path = f"{directorio}/alimentos.db"
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            tablas = {
                # Tablas de alimentos y consumo ELIMINADAS porque ahora las maneja la API.
                
                'peso': '''
                    CREATE TABLE IF NOT EXISTS peso (
                        num INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT,
                        peso REAL
                    )
                ''',
                'agua': '''
                    CREATE TABLE IF NOT EXISTS agua (
                        num INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT,
                        cant INTEGER
                    )
                ''',
                'datos': '''
                    CREATE TABLE IF NOT EXISTS datos (
                        nombre TEXT PRIMARY KEY, # Se mantiene como identificador local si es necesario
                        # estatura INTEGER, <- Eliminada, gestionada por API
                        # nivel_actividad TEXT, <- Eliminada, gestionada por API
                        # genero TEXT, <- Eliminada, gestionada por API
                        # meta_cal INTEGER, <- Eliminada, gestionada por API
                        # edad INTEGER, <- Columna eliminada
                        # fecha_nacimiento DATE, <- Eliminada, gestionada por API
                        recordatorio TEXT, # Específico de la app local
                        cantidad_dias VARCHAR, # Específico de la app local
                        ultimo_msj TEXT, # Específico de la app local
                        profile_pic_path TEXT # Podría ser local o URL de API
                    )
                ''',
                'mensajes': '''
                    CREATE TABLE IF NOT EXISTS mensajes (
                        registrar_alimento INTEGER DEFAULT 0,
                        agregar_alimento INTEGER DEFAULT 0,
                        graficos INTEGER DEFAULT 0,
                        configuracion INTEGER DEFAULT 0,
                        salud INTEGER DEFAULT 0,
                        admin_alimentos INTEGER DEFAULT 0,
                        historial INTEGER DEFAULT 0
                    )
                ''',
                'recordatorios': '''
                    CREATE TABLE IF NOT EXISTS recordatorios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Titulo TEXT,
                        Fecha TEXT,
                        Hora TEXT,
                        Usuario TEXT
                    )
                '''
            }
            
            for tabla in tablas.values():
                cursor.execute(tabla)
                
            cursor.execute("SELECT COUNT(*) FROM mensajes")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO mensajes DEFAULT VALUES")
                
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al crear base de datos local del usuario: {e}")
            return False
        finally:
            if conn:
                conn.close()