#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clase base abstracta para formularios
"""

from abc import ABC, abstractmethod

class FormHandler(ABC):
    @abstractmethod
    def create_form(self):
        pass

    @abstractmethod
    def save(self):
        pass