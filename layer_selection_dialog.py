from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from qgis.core import QgsProject

class LayerSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Layers")

        self.layout = QVBoxLayout()

        # Source Layer
        self.source_layout = QHBoxLayout()
        self.source_label = QLabel("Source Layer:")
        self.source_line_edit = QLineEdit()
        self.source_browse_button = QPushButton("Browse")
        self.source_browse_button.clicked.connect(self.browse_source_layer)
        self.source_layout.addWidget(self.source_label)
        self.source_layout.addWidget(self.source_line_edit)
        self.source_layout.addWidget(self.source_browse_button)

        # Destination Layer
        self.destination_layout = QHBoxLayout()
        self.destination_label = QLabel("Destination Layer:")
        self.destination_line_edit = QLineEdit()
        self.destination_browse_button = QPushButton("Browse")
        self.destination_browse_button.clicked.connect(self.browse_destination_layer)
        self.destination_layout.addWidget(self.destination_label)
        self.destination_layout.addWidget(self.destination_line_edit)
        self.destination_layout.addWidget(self.destination_browse_button)

        # Add layouts to the main layout
        self.layout.addLayout(self.source_layout)
        self.layout.addLayout(self.destination_layout)

        # OK and Cancel buttons
        self.button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

    def browse_source_layer(self):
        layer = self.select_layer()
        if layer:
            self.source_line_edit.setText(layer.name())

    def browse_destination_layer(self):
        layer = self.select_layer()
        if layer:
            self.destination_line_edit.setText(layer.name())

    def select_layer(self):
        layers = QgsProject.instance().mapLayers().values()
        layer_names = [layer.name() for layer in layers]

        dialog = QDialog(self)
        dialog.setWindowTitle("Select Layer")
        dialog_layout = QVBoxLayout()

        combo = QComboBox()
        combo.addItems(layer_names)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        dialog_layout.addWidget(combo)
        dialog_layout.addLayout(button_layout)
        dialog.setLayout(dialog_layout)

        if dialog.exec_() == QDialog.Accepted:
            selected_layer_name = combo.currentText()
            for layer in layers:
                if layer.name() == selected_layer_name:
                    return layer
        return None
    
    def get_layer_by_name(self, layer_name):
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.name() == layer_name:
                return layer
        return None

    def get_source_layer(self):
        layer_name = self.source_line_edit.text()
        return self.get_layer_by_name(layer_name)

    def get_destination_layer(self):
        layer_name = self.destination_line_edit.text()
        return self.get_layer_by_name(layer_name)
