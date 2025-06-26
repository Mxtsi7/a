from PyQt6.QtCore import QRect

class BuscadorManager:
    def __init__(self, parent, entry, listbox, repository):
        self.entry_buscar = entry
        self.coincidencias = listbox
        self.repository = repository
        self.parent = parent
        self.alimentos_buscar = []
        self.match = []
        
        # Conectar eventos
        self.entry_buscar.textChanged.connect(self.obtener_busqueda)
        self.coincidencias.itemClicked.connect(self.on_item_clicked)

    def obtener_busqueda(self):
        typeado = self.entry_buscar.text()
        if not typeado or typeado == '':
            self.alimentos_buscar = []
            self.match = []
        else:
            self.alimentos_buscar = self.repository.cargar_alimentos()
            self.match = [i for i in self.alimentos_buscar if typeado.lower() in i.lower()]
        self.update_coincidencias()

    def update_coincidencias(self):
        self.coincidencias.clear()
        num_coincidencias = len(self.match)
        
        if num_coincidencias > 0:
            # Calcular dimensiones relativas
            parent_width = self.parent.width()
            parent_height = self.parent.height()
            
            height = min(num_coincidencias, 5)
            x = int(parent_width * 0.1)
            y = int(parent_height * 0.4)
            width = int(parent_width * 0.3)
            list_height = int(parent_height * 0.05 * height)
            
            # Posicionar y mostrar el listbox
            self.coincidencias.setGeometry(QRect(x, y, width, list_height))
            self.coincidencias.show()
            
            # Agregar elementos
            for alimento in self.match:
                self.coincidencias.addItem(alimento)
        else:
            self.coincidencias.hide()

    def on_item_clicked(self, item):
        """Maneja el click en un elemento de la lista"""
        self.rellenar_con_texto(item.text())

    def rellenar_con_texto(self, texto):
        """Rellena el entry con el texto seleccionado"""
        self.entry_buscar.clear()
        self.entry_buscar.setText(texto)
        self.coincidencias.hide()

    def rellenar(self, callback):
        """Método para compatibilidad con el callback original"""
        current_item = self.coincidencias.currentItem()
        if current_item:
            alimento_seleccionado = current_item.text()
            self.entry_buscar.clear()
            self.entry_buscar.setText(alimento_seleccionado)
            self.coincidencias.hide()
            callback(alimento_seleccionado)