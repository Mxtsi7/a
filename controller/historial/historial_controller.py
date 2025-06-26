from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QMessageBox
from .historialfacade import HistorialFacade

class HistorialController(QObject):
    # Señales para comunicación con la vista
    data_loaded = pyqtSignal(list)
    statistics_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, usuario, view):
        super().__init__()
        self.usuario = usuario
        self.view = view
        self.facade = HistorialFacade(usuario)
        
        # Conectar señales de la vista con métodos del controlador
        self.view.filtro_aplicado.connect(self.filtrar_por_fecha)
        self.view.filtros_limpiados.connect(self.limpiar_filtros)
        self.view.exportar_solicitado.connect(self.exportar_csv)
        
        # Conectar filtros en tiempo real con un timer para evitar consultas excesivas
        self.filtro_timer = QTimer()
        self.filtro_timer.setSingleShot(True)
        self.filtro_timer.timeout.connect(self.filtrar_en_tiempo_real)
        
        self.view.search_input.textChanged.connect(self.iniciar_filtro_timer)
        self.view.meal_filter.currentTextChanged.connect(self.iniciar_filtro_timer)
    
    def iniciar_filtro_timer(self):
        """Iniciar timer para filtrado en tiempo real"""
        self.filtro_timer.stop()
        self.filtro_timer.start(300)  # 300ms de delay
    
    def cargar_historial_inicial(self):
        """Cargar historial completo inicial"""
        try:
            registros = self.facade.obtener_todos_los_registros()
            self.view.update_table_data(registros)
            self.calcular_estadisticas(registros)
        except Exception as e:
            error_msg = f"Error al cargar historial: {e}"
            print(error_msg)
            self.view.show_error_message(error_msg)

    def filtrar_por_fecha(self):
        """Filtrar historial por rango de fechas"""
        try:
            fecha_desde = self.view.date_from.date().toPython().strftime('%Y-%m-%d')
            fecha_hasta = self.view.date_to.date().toPython().strftime('%Y-%m-%d')
            
            registros = self.facade.obtener_registros_por_rango_fecha(fecha_desde, fecha_hasta)
            
            # Aplicar filtros adicionales (búsqueda y momento del día)
            registros_filtrados = self.aplicar_filtros_adicionales(registros)
            
            self.view.update_table_data(registros_filtrados)
            self.calcular_estadisticas(registros_filtrados)
            
        except Exception as e:
            error_msg = f"Error al filtrar por fecha: {e}"
            print(error_msg)
            self.view.show_error_message(error_msg)
    
    def filtrar_en_tiempo_real(self):
        """Filtrar datos en tiempo real según texto de búsqueda y momento del día"""
        try:
            # Obtener rango de fechas actual
            fecha_desde = self.view.date_from.date().toPython().strftime('%Y-%m-%d')
            fecha_hasta = self.view.date_to.date().toPython().strftime('%Y-%m-%d')
            
            # Obtener registros del rango de fechas
            registros = self.facade.obtener_registros_por_rango_fecha(fecha_desde, fecha_hasta)
            
            # Aplicar filtros adicionales
            registros_filtrados = self.aplicar_filtros_adicionales(registros)
            
            self.view.update_table_data(registros_filtrados)
            self.calcular_estadisticas(registros_filtrados)
            
        except Exception as e:
            error_msg = f"Error al filtrar en tiempo real: {e}"
            print(error_msg)
            self.view.show_error_message(error_msg)
    
    def aplicar_filtros_adicionales(self, registros):
        """Aplicar filtros de búsqueda y momento del día"""
        texto_busqueda = self.view.search_input.text().lower()
        momento_dia = self.view.meal_filter.currentText()
        
        registros_filtrados = []
        
        for registro in registros:
            nombre_alimento = str(registro[0]).lower()
            momento_registro = str(registro[6]) if len(registro) > 6 else "Otro"
            
            # Filtro por texto de búsqueda
            if texto_busqueda and texto_busqueda not in nombre_alimento:
                continue
            
            # Filtro por momento del día
            if momento_dia != "Todos" and momento_registro != momento_dia:
                continue
            
            registros_filtrados.append(registro)
        
        return registros_filtrados
    
    def limpiar_filtros(self):
        """Limpiar todos los filtros y recargar datos completos"""
        try:
            # Los filtros ya se limpian en la vista
            # Recargar datos completos
            self.cargar_historial_inicial()
            
        except Exception as e:
            error_msg = f"Error al limpiar filtros: {e}"
            print(error_msg)
            self.view.show_error_message(error_msg)
    
    def calcular_estadisticas(self, registros):
        """Calcular estadísticas de los registros actuales"""
        try:
            if not registros:
                estadisticas = {
                    'total_calorias': 0,
                    'total_alimentos': 0,
                    'promedio_diario': 0
                }
            else:
                total_calorias = sum(float(registro[3]) for registro in registros)
                total_alimentos = len(registros)
                
                # Calcular días únicos para promedio diario
                fechas_unicas = set(registro[4] for registro in registros)
                dias_count = len(fechas_unicas) if fechas_unicas else 1
                promedio_diario = total_calorias / dias_count
                
                estadisticas = {
                    'total_calorias': total_calorias,
                    'total_alimentos': total_alimentos,
                    'promedio_diario': promedio_diario
                }
            
            self.view.update_statistics_display(estadisticas)
            
        except Exception as e:
            error_msg = f"Error al calcular estadísticas: {e}"
            print(error_msg)
            self.view.show_error_message(error_msg)
    
    def exportar_csv(self):
        """Exportar datos actuales a CSV"""
        try:
            # Usar el método de exportación de la vista
            self.view.export_to_csv()
            
        except Exception as e:
            error_msg = f"Error al exportar CSV: {e}"
            print(error_msg)
            self.view.show_error_message(error_msg)
    
    def mostrar_estadisticas_fecha(self, fecha_str):
        """Mostrar estadísticas para una fecha específica"""
        try:
            estadisticas = self.facade.obtener_estadisticas_fecha(fecha_str)
            
            mensaje = f"""Estadísticas del {fecha_str}:
            Total de calorías: {estadisticas['total_calorias']:.1f}
            Total de alimentos: {estadisticas['total_alimentos']}
            Promedio por alimento: {estadisticas['promedio_calorias']:.1f} cal"""
            
            QMessageBox.information(self.view, "Estadísticas del Día", mensaje)
            
        except Exception as e:
            error_msg = f"Error al obtener estadísticas: {e}"
            print(error_msg)
            self.view.show_error_message(error_msg)
    
    def agregar_registro_consumo(self, nombre_alimento, cantidad, calorias, momento_dia):
        """Agregar nuevo registro de consumo"""
        try:
            # Recargar datos después de agregar
            self.cargar_historial_inicial()
            
        except Exception as e:
            error_msg = f"Error al agregar registro: {e}"
            print(error_msg)
            self.view.show_error_message(error_msg)
    
    def cleanup(self):
        """Limpiar recursos"""
        try:
            if hasattr(self, 'filtro_timer'):
                self.filtro_timer.stop()
            self.facade.cleanup()
        except Exception as e:
            print(f"Error durante cleanup: {e}")