#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de planificación de menús semanales
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QTableWidget, QTableWidgetItem,
                             QComboBox, QTextEdit, QGridLayout, QScrollArea,
                             QHeaderView, QAbstractItemView, QMessageBox,
                             QDialog, QDialogButtonBox, QListWidget, QSplitter,
                             QFileDialog, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import random
import json
from datetime import datetime

class AddMealDialog(QDialog):
    """Diálogo para agregar comida al menú"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_food = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Agregar Comida al Menú")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #3c3c3c;
                color: white;
            }
            QListWidget {
                background-color: #555;
                border: 1px solid #777;
                border-radius: 5px;
                color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #666;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Lista de alimentos
        layout.addWidget(QLabel("Selecciona un alimento:"))
        self.food_list = QListWidget()
        
        # Alimentos de ejemplo
        foods = [
            "Pollo a la plancha - 165 kcal/100g",
            "Arroz blanco - 130 kcal/100g",
            "Ensalada mixta - 45 kcal/100g",
            "Salmón grillado - 208 kcal/100g",
            "Pasta integral - 124 kcal/100g",
            "Verduras al vapor - 25 kcal/100g",
            "Pechuga de pavo - 135 kcal/100g",
            "Quinoa - 120 kcal/100g",
            "Brócoli - 34 kcal/100g",
            "Aguacate - 160 kcal/100g",
            "Atún en agua - 116 kcal/100g",
            "Yogur griego - 59 kcal/100g",
            "Huevos - 155 kcal/100g",
            "Lentejas - 116 kcal/100g",
            "Espinacas - 23 kcal/100g"
        ]
        
        for food in foods:
            self.food_list.addItem(food)
        
        layout.addWidget(self.food_list)
        
        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def accept(self):
        current_item = self.food_list.currentItem()
        if current_item:
            self.selected_food = current_item.text()
        super().accept()

class Menu(QWidget):
    def __init__(self):
        super().__init__()
        self.menu_data = {}
        self.init_ui()
        self.load_sample_menu()
        
    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #3c3c3c;
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QComboBox, QTextEdit {
                background-color: #555;
                border: 1px solid #777;
                border-radius: 5px;
                padding: 8px;
                color: white;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTableWidget {
                background-color: #555;
                alternate-background-color: #606060;
                gridline-color: #777;
                selection-background-color: #4CAF50;
            }
            QHeaderView::section {
                background-color: #666;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #777;
            }
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                text-align: center;
                background-color: #444;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("Planificador de Menús Semanales")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Controles superiores
        controls_group = self.create_controls_group()
        layout.addWidget(controls_group)
        
        # Splitter para dividir la vista
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Tabla de menú semanal
        menu_widget = self.create_menu_table()
        splitter.addWidget(menu_widget)
        
        # Panel de información nutricional
        nutrition_widget = self.create_nutrition_panel()
        splitter.addWidget(nutrition_widget)
        
        # Configurar proporciones del splitter
        splitter.setSizes([600, 300])
        layout.addWidget(splitter)
        
        # Lista de compras
        shopping_group = self.create_shopping_list_group()
        layout.addWidget(shopping_group)
        
    def create_controls_group(self):
        """Crear grupo de controles"""
        group = QGroupBox("Controles de Menú")
        layout = QHBoxLayout(group)
        
        # Selector de semana
        layout.addWidget(QLabel("Semana:"))
        self.week_combo = QComboBox()
        self.week_combo.addItems(["Semana Actual", "Próxima Semana", "Semana Personalizada"])
        layout.addWidget(self.week_combo)
        
        layout.addStretch()
        
        # Botones de acción
        generate_btn = QPushButton("Generar Menú Automático")
        generate_btn.clicked.connect(self.generate_automatic_menu)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        layout.addWidget(generate_btn)
        
        clear_btn = QPushButton("Limpiar Menú")
        clear_btn.clicked.connect(self.clear_menu)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        layout.addWidget(clear_btn)
        
        save_btn = QPushButton("Guardar Menú")
        save_btn.clicked.connect(self.save_menu)
        layout.addWidget(save_btn)
        
        load_btn = QPushButton("Cargar Menú")
        load_btn.clicked.connect(self.load_menu)
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        layout.addWidget(load_btn)
        
        return group
    
    def create_menu_table(self):
        """Crear tabla de menú semanal"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Título
        title = QLabel("Menú Semanal")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Tabla
        self.menu_table = QTableWidget()
        self.menu_table.setRowCount(7)  # 7 días
        self.menu_table.setColumnCount(4)  # Desayuno, Almuerzo, Merienda, Cena
        
        # Headers
        days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meals = ["Desayuno", "Almuerzo", "Merienda", "Cena"]
        
        self.menu_table.setVerticalHeaderLabels(days)
        self.menu_table.setHorizontalHeaderLabels(meals)
        
        # Configurar tabla
        self.menu_table.setAlternatingRowColors(True)
        self.menu_table.cellDoubleClicked.connect(self.edit_meal)
        
        # Ajustar tamaño de columnas
        header = self.menu_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Ajustar altura de filas
        for i in range(7):
            self.menu_table.setRowHeight(i, 60)
        
        layout.addWidget(self.menu_table)
        
        return widget
    
    def create_nutrition_panel(self):
        """Crear panel de información nutricional"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Título
        title = QLabel("Información Nutricional")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Selector de día
        day_layout = QHBoxLayout()
        day_layout.addWidget(QLabel("Día:"))
        self.day_combo = QComboBox()
        self.day_combo.addItems(["Lunes", "Martes", "Miércoles", "Jueves", 
                                "Viernes", "Sábado", "Domingo"])
        self.day_combo.currentTextChanged.connect(self.update_nutrition_info)
        day_layout.addWidget(self.day_combo)
        day_layout.addStretch()
        layout.addLayout(day_layout)
        
        # Barras de progreso nutricional
        progress_group = QGroupBox("Objetivos Diarios")
        progress_layout = QVBoxLayout(progress_group)
        
        # Calorías
        calories_layout = QHBoxLayout()
        calories_layout.addWidget(QLabel("Calorías:"))
        self.calories_progress = QProgressBar()
        self.calories_progress.setMaximum(2000)
        self.calories_progress.setValue(0)
        calories_layout.addWidget(self.calories_progress)
        self.calories_value_label = QLabel("0/2000 kcal")
        calories_layout.addWidget(self.calories_value_label)
        progress_layout.addLayout(calories_layout)
        
        # Proteínas
        protein_layout = QHBoxLayout()
        protein_layout.addWidget(QLabel("Proteínas:"))
        self.protein_progress = QProgressBar()
        self.protein_progress.setMaximum(150)
        self.protein_progress.setValue(0)
        protein_layout.addWidget(self.protein_progress)
        self.protein_value_label = QLabel("0/150g")
        protein_layout.addWidget(self.protein_value_label)
        progress_layout.addLayout(protein_layout)
        
        # Carbohidratos
        carbs_layout = QHBoxLayout()
        carbs_layout.addWidget(QLabel("Carbohidratos:"))
        self.carbs_progress = QProgressBar()
        self.carbs_progress.setMaximum(275)
        self.carbs_progress.setValue(0)
        carbs_layout.addWidget(self.carbs_progress)
        self.carbs_value_label = QLabel("0/275g")
        carbs_layout.addWidget(self.carbs_value_label)
        progress_layout.addLayout(carbs_layout)
        
        # Grasas
        fats_layout = QHBoxLayout()
        fats_layout.addWidget(QLabel("Grasas:"))
        self.fats_progress = QProgressBar()
        self.fats_progress.setMaximum(67)
        self.fats_progress.setValue(0)
        fats_layout.addWidget(self.fats_progress)
        self.fats_value_label = QLabel("0/67g")
        fats_layout.addWidget(self.fats_value_label)
        progress_layout.addLayout(fats_layout)
        
        layout.addWidget(progress_group)
        
        # Información nutricional detallada
        nutrition_group = QGroupBox("Resumen del Día")
        nutrition_layout = QVBoxLayout(nutrition_group)
        
        self.calories_label = QLabel("Calorías Totales: 0 kcal")
        self.protein_label = QLabel("Proteínas: 0g")
        self.carbs_label = QLabel("Carbohidratos: 0g")
        self.fats_label = QLabel("Grasas: 0g")
        
        nutrition_layout.addWidget(self.calories_label)
        nutrition_layout.addWidget(self.protein_label)
        nutrition_layout.addWidget(self.carbs_label)
        nutrition_layout.addWidget(self.fats_label)
        
        layout.addWidget(nutrition_group)
        
        # Recomendaciones
        recommendations_group = QGroupBox("Recomendaciones")
        recommendations_layout = QVBoxLayout(recommendations_group)
        
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setMaximumHeight(100)
        self.recommendations_text.setReadOnly(True)
        recommendations_layout.addWidget(self.recommendations_text)
        
        layout.addWidget(recommendations_group)
        
        layout.addStretch()
        
        return widget
    
    def create_shopping_list_group(self):
        """Crear grupo de lista de compras"""
        group = QGroupBox("Lista de Compras Generada")
        layout = QVBoxLayout(group)
        
        # Controles
        controls_layout = QHBoxLayout()
        
        generate_list_btn = QPushButton("Generar Lista de Compras")
        generate_list_btn.clicked.connect(self.generate_shopping_list)
        generate_list_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        controls_layout.addWidget(generate_list_btn)
        
        export_list_btn = QPushButton("Exportar Lista")
        export_list_btn.clicked.connect(self.export_shopping_list)
        controls_layout.addWidget(export_list_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Lista de compras
        self.shopping_list_text = QTextEdit()
        self.shopping_list_text.setMaximumHeight(120)
        self.shopping_list_text.setPlaceholderText("La lista de compras aparecerá aquí...")
        layout.addWidget(self.shopping_list_text)
        
        return group
    
    def load_sample_menu(self):
        """Cargar menú de ejemplo"""
        sample_meals = {
            "Desayuno": ["Avena con frutas", "Tostadas integrales", "Yogur con granola", 
                        "Huevos revueltos", "Smoothie verde", "Cereales integrales", "Tortilla francesa"],
            "Almuerzo": ["Pollo a la plancha", "Salmón grillado", "Ensalada César", 
                        "Pasta con verduras", "Arroz con pollo", "Quinoa con vegetales", "Lentejas guisadas"],
            "Merienda": ["Fruta fresca", "Yogur natural", "Frutos secos", 
                        "Batido de proteínas", "Tostada con aguacate", "Té con galletas", "Smoothie de frutas"],
            "Cena": ["Pescado al horno", "Ensalada mixta", "Sopa de verduras", 
                    "Pollo al curry", "Verduras grilladas", "Tortilla de espinacas", "Crema de calabaza"]
        }
        
        days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meals = ["Desayuno", "Almuerzo", "Merienda", "Cena"]
        
        for day_idx, day in enumerate(days):
            for meal_idx, meal in enumerate(meals):
                food = random.choice(sample_meals[meal])
                calories = random.randint(200, 600)
                item = QTableWidgetItem(f"{food}\n{calories} kcal")
                item.setTextAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                self.menu_table.setItem(day_idx, meal_idx, item)
        
        self.update_nutrition_info()
    
    def edit_meal(self, row, column):
        """Editar comida en el menú"""
        dialog = AddMealDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_food:
            # Extraer nombre y calorías
            food_info = dialog.selected_food
            food_name = food_info.split(" - ")[0]
            calories_info = food_info.split(" - ")[1]
            calories = int(calories_info.split(" ")[0])
            
            # Actualizar celda
            item = QTableWidgetItem(f"{food_name}\n{calories} kcal")
            item.setTextAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            self.menu_table.setItem(row, column, item)
            
            self.update_nutrition_info()
    
    def generate_automatic_menu(self):
        """Generar menú automático"""
        self.load_sample_menu()
        QMessageBox.information(self, "Menú Generado", 
                               "Se ha generado un menú automático balanceado para la semana.")
    
    def clear_menu(self):
        """Limpiar menú"""
        for i in range(7):
            for j in range(4):
                self.menu_table.setItem(i, j, QTableWidgetItem(""))
        self.update_nutrition_info()
    
    def save_menu(self):
        """Guardar menú"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Guardar Menú", 
                f"menu_{datetime.now().strftime('%Y%m%d')}.json",
                "JSON Files (*.json)"
            )
            
            if filename:
                menu_data = {}
                days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                meals = ["Desayuno", "Almuerzo", "Merienda", "Cena"]
                
                for day_idx, day in enumerate(days):
                    menu_data[day] = {}
                    for meal_idx, meal in enumerate(meals):
                        item = self.menu_table.item(day_idx, meal_idx)
                        if item and item.text():
                            menu_data[day][meal] = item.text()
                        else:
                            menu_data[day][meal] = ""
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(menu_data, f, ensure_ascii=False, indent=4)
                
                QMessageBox.information(self, "Menú Guardado", 
                                       f"El menú ha sido guardado exitosamente en:\n{filename}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al guardar el menú:\n{str(e)}")
    
    def load_menu(self):
        """Cargar menú desde archivo"""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Cargar Menú",
                "",
                "JSON Files (*.json)"
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    menu_data = json.load(f)
                
                days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                meals = ["Desayuno", "Almuerzo", "Merienda", "Cena"]
                
                for day_idx, day in enumerate(days):
                    for meal_idx, meal in enumerate(meals):
                        if day in menu_data and meal in menu_data[day]:
                            text = menu_data[day][meal]
                            item = QTableWidgetItem(text)
                            item.setTextAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                            self.menu_table.setItem(day_idx, meal_idx, item)
                
                self.update_nutrition_info()
                QMessageBox.information(self, "Menú Cargado", "El menú ha sido cargado exitosamente.")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar el menú:\n{str(e)}")
    
    def update_nutrition_info(self):
        """Actualizar información nutricional del día seleccionado"""
        day = self.day_combo.currentText()
        day_index = ["Lunes", "Martes", "Miércoles", "Jueves", 
                    "Viernes", "Sábado", "Domingo"].index(day)
        
        total_calories = 0
        
        # Calcular calorías del día
        for meal_idx in range(4):
            item = self.menu_table.item(day_index, meal_idx)
            if item and item.text():
                try:
                    lines = item.text().split('\n')
                    if len(lines) > 1 and 'kcal' in lines[1]:
                        calories = int(lines[1].split(' ')[0])
                        total_calories += calories
                except:
                    pass
        
        # Calcular macronutrientes (estimación)
        protein = int(total_calories * 0.15 / 4)
        carbs = int(total_calories * 0.55 / 4)
        fats = int(total_calories * 0.30 / 9)
        
        # Actualizar barras de progreso
        self.calories_progress.setValue(min(total_calories, 2000))
        self.protein_progress.setValue(min(protein, 150))
        self.carbs_progress.setValue(min(carbs, 275))
        self.fats_progress.setValue(min(fats, 67))
        
        # Actualizar labels de valores
        self.calories_value_label.setText(f"{total_calories}/2000 kcal")
        self.protein_value_label.setText(f"{protein}/150g")
        self.carbs_value_label.setText(f"{carbs}/275g")
        self.fats_value_label.setText(f"{fats}/67g")
        
        # Actualizar labels de resumen
        self.calories_label.setText(f"Calorías Totales: {total_calories} kcal")
        self.protein_label.setText(f"Proteínas: {protein}g")
        self.carbs_label.setText(f"Carbohidratos: {carbs}g")
        self.fats_label.setText(f"Grasas: {fats}g")
        
        # Generar recomendaciones
        recommendations = []
        if total_calories < 1200:
            recommendations.append("• Las calorías están por debajo del mínimo recomendado.")
        elif total_calories > 2500:
            recommendations.append("• Las calorías están por encima del recomendado para la mayoría de adultos.")
        else:
            recommendations.append("• El balance calórico del día se ve adecuado.")
        
        if total_calories > 0:
            if protein < 100:
                recommendations.append("• Considera aumentar la ingesta de proteínas.")
            if carbs > 300:
                recommendations.append("• Podrías reducir los carbohidratos.")
            recommendations.append("• Asegúrate de incluir variedad de frutas y verduras.")
            recommendations.append("• Mantén una hidratación adecuada durante el día.")
        
        self.recommendations_text.setText("\n".join(recommendations))
    
    def generate_shopping_list(self):
        """Generar lista de compras basada en el menú"""
        ingredients = set()
        
        # Extraer ingredientes del menú (simulado)
        base_ingredients = [
            "Pollo", "Pescado", "Huevos", "Leche", "Yogur",
            "Avena", "Pan integral", "Arroz", "Pasta", "Quinoa",
            "Lechuga", "Tomate", "Cebolla", "Brócoli", "Espinacas",
            "Manzanas", "Plátanos", "Fresas", "Aguacate",
            "Aceite de oliva", "Sal", "Pimienta", "Ajo"
        ]
        
        # Seleccionar ingredientes aleatorios
        selected_ingredients = random.sample(base_ingredients, k=random.randint(12, 18))
        
        shopping_list = "LISTA DE COMPRAS SEMANAL\n" + "="*30 + "\n\n"
        shopping_list += f"Generada el: {datetime.now().strftime('%d/%m/%Y')}\n\n"
        
        categories = {
            "Proteínas": ["Pollo", "Pescado", "Huevos"],
            "Lácteos": ["Leche", "Yogur"],
            "Cereales": ["Avena", "Pan integral", "Arroz", "Pasta", "Quinoa"],
            "Verduras": ["Lechuga", "Tomate", "Cebolla", "Brócoli", "Espinacas"],
            "Frutas": ["Manzanas", "Plátanos", "Fresas", "Aguacate"],
            "Condimentos": ["Aceite de oliva", "Sal", "Pimienta", "Ajo"]
        }
        
        for category, items in categories.items():
            category_items = [item for item in selected_ingredients if item in items]
            if category_items:
                shopping_list += f"{category}:\n"
                for item in category_items:
                    shopping_list += f"  • {item}\n"
                shopping_list += "\n"
        
        self.shopping_list_text.setText(shopping_list)
    
    def export_shopping_list(self):
        """Exportar lista de compras"""
        if not self.shopping_list_text.toPlainText():
            QMessageBox.warning(self, "Lista Vacía", "Primero genera una lista de compras.")
            return
        
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar Lista de Compras",
                f"lista_compras_{datetime.now().strftime('%Y%m%d')}.txt",
                "Text Files (*.txt)"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.shopping_list_text.toPlainText())
                
                QMessageBox.information(self, "Lista Exportada", 
                                       f"La lista ha sido exportada exitosamente en:\n{filename}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al exportar la lista:\n{str(e)}")