from abc import ABC, abstractmethod

class AlimentoRepository(ABC):
    @abstractmethod
    def get_ultimo_insertado(self):
        pass

    @abstractmethod
    def buscar_alimento_en_db(self, nombre_alimento):
        pass

    @abstractmethod
    def cargar_alimentos(self):
        pass

    @abstractmethod
    def calcular_calorias_totales(self):
        pass

    @abstractmethod
    def insert_alimento(self, nombre, fecha, hora, cantidad, calorias):
        pass

    @abstractmethod
    def actualizar_calorias_totales(self):
        pass