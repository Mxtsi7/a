#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formularios de Login convertidos a PyQt6
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QPushButton,QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from model.login.auth_service import ApiService 
from model.util.colores import *
from .form import *

class LoginForm(IForm, QWidget):

    iniciar_sesion_clicked = pyqtSignal()
    registrarse_clicked = pyqtSignal()

    def __init__(self, ventana_principal, auth_service: ApiService, on_success):
        super().__init__()
        self.ventana_principal = ventana_principal
        self.auth_service = auth_service
        self.on_success = on_success
        self.widgets = {}
        self.init_ui()
    
    # El resto del archivo no necesita cambios lógicos.
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)
        self.frame = QFrame()
        self.frame.setStyleSheet(f"QFrame {{ background-color: {gris}; border: 2px solid {azul_medio_oscuro}; border-radius: 20px; padding: 20px; }}")
        self.frame.setFixedSize(400, 300)
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.setSpacing(20)
        titulo = QLabel("Bienvenido")
        titulo.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        titulo.setStyleSheet(f"color: {azul_medio_oscuro};")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(titulo)
        btn_style = f"QPushButton {{ background-color: {verde_boton}; color: {azul_medio_oscuro}; border: none; border-radius: 20px; font: bold 18px Arial; padding: 15px; min-width: 170px; min-height: 50px; }} QPushButton:hover {{ background-color: {verde_oscuro}; }}"
        self.widgets['btn_iniciar'] = QPushButton('Iniciar Sesión')
        self.widgets['btn_iniciar'].setStyleSheet(btn_style)
        self.widgets['btn_iniciar'].clicked.connect(self._mostrar_iniciar_sesion)
        frame_layout.addWidget(self.widgets['btn_iniciar'])
        self.widgets['btn_registrarse'] = QPushButton('Registrarse')
        self.widgets['btn_registrarse'].setStyleSheet(btn_style)
        self.widgets['btn_registrarse'].clicked.connect(self._mostrar_registro)
        frame_layout.addWidget(self.widgets['btn_registrarse'])
        main_layout.addWidget(self.frame)
    def mostrar(self): self.show()
    def ocultar(self): self.hide()
    def _mostrar_iniciar_sesion(self): self.iniciar_sesion_clicked.emit()
    def _mostrar_registro(self): self.registrarse_clicked.emit()