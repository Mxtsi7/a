# model/database_manager.py

import sqlite3
import os
from datetime import datetime, date

# Necesitamos timedelta para "Última semana"
from datetime import timedelta

class ChartDataManager:
    """
    Se encarga de obtener y procesar los datos para los gráficos
    de la base de datos específica de un usuario.
    """
    def __init__(self, username: str):
        if not username:
            raise ValueError("El nombre de usuario no puede estar vacío.")
        
        self.username = username
        self.db_path = os.path.join("users", self.username, "alimentos.db")

    def _get_start_date(self, period: str) -> str:
        """
        Calcula la fecha de inicio basado en la lógica de calendario especificada.
        """
        today = date.today() # Usamos date para simplicidad en los cálculos de calendario
        
        start_date = today - timedelta(days=7) # Valor por defecto

        if period == "Última semana":
            # Mantenemos los últimos 7 días desde hoy.
            start_date = today - timedelta(days=7)
        
        elif period == "Último mes":
            # El primer día del mes actual.
            start_date = today.replace(day=1)
            
        elif period == "Últimos 3 meses":
            # Calculamos el inicio de hace dos meses para incluir el actual y los dos anteriores.
            current_year = today.year
            current_month = today.month
            
            # Restamos 2 meses. Python maneja el cambio de año automáticamente.
            start_month = current_month - 2
            start_year = current_year
            if start_month <= 0:
                start_month += 12
                start_year -= 1
            
            start_date = date(start_year, start_month, 1)

        elif period == "Último año":
            # El primer día del año actual.
            start_date = today.replace(month=1, day=1)
        
        # Devolvemos la fecha en el formato que SQLite entiende para comparar.
        return start_date.strftime("%Y-%m-%d")

    def _execute_query(self, query: str, params: tuple):
        """Ejecuta una consulta y devuelve todos los resultados."""
        if not os.path.exists(self.db_path):
            print(f"Error: No se encontró la base de datos en la ruta: {self.db_path}")
            return []
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error en la base de datos '{self.db_path}': {e}")
            return []

    def _get_aggregated_data(self, table_name: str, value_column: str, aggregation_func: str, period: str) -> tuple[list, list]:
        """
        Función genérica y robusta para obtener datos agregados, corrigiendo el formato de fecha.
        """
        start_date = self._get_start_date(period)

        # La reconstrucción manual de la fecha sigue siendo necesaria y correcta.
        reformatted_date = "SUBSTR(fecha, 7, 4) || '-' || SUBSTR(fecha, 4, 2) || '-' || SUBSTR(fecha, 1, 2)"
        
        query = f"""
            SELECT 
                {reformatted_date}, 
                {aggregation_func}({value_column}) 
            FROM {table_name}
            WHERE {reformatted_date} >= ?
            GROUP BY {reformatted_date}
            ORDER BY {reformatted_date} ASC
        """
        
        results = self._execute_query(query, (start_date,))
        
        if not results:
            return [], []

        labels = [datetime.strptime(row[0], "%Y-%m-%d").strftime("%d/%m") for row in results]
        data = [row[1] for row in results]
        
        return labels, data

    def get_calories_data(self, period: str) -> tuple[list, list]:
        return self._get_aggregated_data("consumo_diario", "total_cal", "SUM", period)

    def get_water_data(self, period: str) -> tuple[list, list]:
        return self._get_aggregated_data("agua", "cant", "SUM", period)

    def get_weight_data(self, period: str) -> tuple[list, list]:
        return self._get_aggregated_data("peso", "peso", "AVG", period)