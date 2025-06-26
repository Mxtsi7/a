import sqlite3

def _obtener_conexion(usuario):
    """Obtiene una conexión a la base de datos del usuario"""
    return sqlite3.connect(f"./users/{usuario}/alimentos.db")