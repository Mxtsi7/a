import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox
from .repositorio_abs import AlimentoRepository

class SQLiteAlimentoRepository(AlimentoRepository):
    def __init__(self, usuario):
        self.usuario = usuario

    def get_ultimo_insertado(self):
        conn = sqlite3.connect(f"./users/{self.usuario}/alimentos.db")
        cursor = conn.cursor()
        query = "SELECT nombre FROM consumo_diario WHERE id = (SELECT MAX(id) FROM consumo_diario);"
        cursor.execute(query)
        ultimo = cursor.fetchone()
        conn.close()
        return ultimo[0] if ultimo else 'Agrega un alimento!'

    def buscar_alimento_en_db(self, nombre_alimento):
        conn = sqlite3.connect(f"./users/{self.usuario}/alimentos.db")
        cursor = conn.cursor()
        query = "SELECT nombre, calorias_100gr, calorias_porcion FROM alimento WHERE nombre = ?"
        cursor.execute(query, (nombre_alimento,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado

    def cargar_alimentos(self):
        conn = sqlite3.connect(f"./users/{self.usuario}/alimentos.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM alimento")
        alimentos = cursor.fetchall()
        lista_alimentos = [alimento[0] for alimento in alimentos if alimento[0] is not None]
        conn.close()
        return lista_alimentos

    def calcular_calorias_totales(self):
        conn = sqlite3.connect(f"./users/{self.usuario}/alimentos.db")
        cursor = conn.cursor()
        fecha_actual = datetime.now().strftime('%d-%m-%Y')
        query = '''
        SELECT SUM(total_cal) FROM consumo_diario WHERE fecha = ?
        '''
        cursor.execute(query, (fecha_actual,))
        resultado = cursor.fetchone()[0]
        conn.close()
        return resultado if resultado else 0

    def insert_alimento(self, nombre, fecha, hora, cantidad, calorias):
        conn = sqlite3.connect(f"./users/{self.usuario}/alimentos.db")
        cursor = conn.cursor()
        insert_query = '''
        INSERT INTO consumo_diario (nombre, fecha, hora, cantidad, total_cal)
        VALUES (?, ?, ?, ?, ?);
        '''
        update_query = '''
        UPDATE consumo_diario
        SET cantidad = cantidad + ?, total_cal = total_cal + ?
        WHERE nombre = ? AND fecha = ?;
        '''
        cursor.execute('SELECT cantidad, total_cal FROM consumo_diario WHERE nombre = ? AND fecha = ?', (nombre, fecha))
        resultado = cursor.fetchone()
        if resultado:
            cursor.execute(update_query, (cantidad, calorias, nombre, fecha))
        else:
            cursor.execute(insert_query, (nombre, fecha, hora, cantidad, calorias))
        conn.commit()
        
        # Crear y mostrar mensaje de éxito con PyQt6
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Registro exitoso")
        msg_box.setText(f"Alimento {nombre} registrado con éxito.")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        
        conn.close()

    def actualizar_calorias_totales(self):
        pass  # Handled by UI updates