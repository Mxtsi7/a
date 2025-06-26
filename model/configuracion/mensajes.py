from PyQt6.QtWidgets import QMessageBox

class MessageHandler:
    @staticmethod
    def mostrar_info(titulo, mensaje):
        """Muestra un cuadro de diálogo informativo de PyQt6."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(mensaje)
        msg_box.setWindowTitle(titulo)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @staticmethod
    def mostrar_advertencia(titulo, mensaje):
        """Muestra un cuadro de diálogo de advertencia de PyQt6."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText(mensaje)
        msg_box.setWindowTitle(titulo)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @staticmethod
    def confirmar_accion(titulo, mensaje):
        """
        Muestra un cuadro de diálogo de confirmación (Sí/No) de PyQt6.
        Devuelve 'Sí' o 'No' para mantener la compatibilidad con el código original.
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning) # O podrías usar QMessageBox.Icon.Question
        msg_box.setText(mensaje)
        msg_box.setWindowTitle(titulo)
        # Se establecen los botones traducidos para una mejor UX
        yes_button = msg_box.addButton("Sí", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("No", QMessageBox.ButtonRole.NoRole)
        msg_box.setDefaultButton(no_button)
        
        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            return "Sí"
        return "No"