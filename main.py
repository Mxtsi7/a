#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contador de Calorías Pro 60Hz
Aplicación principal que inicializa AMBAS APIs y la interfaz gráfica.
"""
    
import sys
import multiprocessing
import uvicorn
from PyQt6.QtWidgets import QApplication

# --- 1. Importar ambas aplicaciones FastAPI ---
# Se renombra cada 'app' para evitar conflictos de nombres.
from controller.API.user.api_server import app as user_api_app
from api_alimento import app as alimento_api_app
from view.ventana_main.ventana_principal import MainWindow

# --- 2. Crear una función de ejecución para CADA API ---

def run_user_api():
    """Función para correr la API de Usuarios en el puerto 8000."""
    print("Iniciando servidor API de Usuarios en segundo plano en http://127.0.0.1:8000")
    uvicorn.run(user_api_app, host="127.0.0.1", port=8000)

def run_alimento_api():
    """Función para correr la API de Alimentos en el puerto 8001."""
    print("Iniciando servidor API de Alimentos en segundo plano en http://127.0.0.1:8001")
    uvicorn.run(alimento_api_app, host="127.0.0.1", port=8001)


def main():
    # --- 3. Iniciar AMBAS APIs en procesos separados ---
    # Los procesos se marcan como 'daemon' para que se cierren automáticamente
    # cuando la aplicación principal (PyQt) se cierre.
    
    print("Iniciando procesos de APIs...")
    user_api_process = multiprocessing.Process(target=run_user_api, daemon=True)
    alimento_api_process = multiprocessing.Process(target=run_alimento_api, daemon=True)
    
    user_api_process.start()
    alimento_api_process.start()
    print("APIs iniciadas con éxito.")
    
    # Inicializar la aplicación de PyQt
    app = QApplication(sys.argv)

    # Configurar estilo de la aplicación
    app.setStyle('Fusion')
    
    # Crear y mostrar la ventana principal
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    # Necesario para que multiprocessing funcione correctamente en algunos S.O.
    multiprocessing.freeze_support()
    main()