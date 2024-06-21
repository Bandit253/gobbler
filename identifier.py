
from qgis.gui import QgsMapToolIdentifyFeature, QgsRubberBand, QgsHighlight
from qgis.core import QgsProject, QgsMessageLog, Qgis, QgsFeature, QgsWkbTypes
from qgis.PyQt.QtCore import  Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor

class IdentifyTool(QgsMapToolIdentifyFeature):
    featureIdentified = pyqtSignal(QgsFeature)

    def __init__(self, canvas, layer, isSource):
        super().__init__(canvas)
        self.canvas = canvas
        self.layer = layer
        self.isSource = isSource

    def canvasReleaseEvent(self, event):
        if self.isSource:
            colour = QColor(255, 0, 0)
            self.clear_highlights(colour)        
        else:
            colour = QColor(0, 255, 0)
            self.clear_highlights(colour)
            
        results = self.identify(event.x(), event.y(), self.TopDownStopAtFirst, [self.layer])
        if results:
            feature = results[0].mFeature
            self.featureIdentified.emit(feature)
            highlight = QgsHighlight(self.canvas, feature.geometry(), self.layer)
            highlight.setWidth(4)
            highlight.setColor(colour)        
            highlight.show()

                    
    def clear_highlights(self, colour):
        """ Removes highlight objects from the map canvas """
        for item in self.canvas.scene().items():
            if isinstance(item, QgsHighlight):
                if item.color() == colour:
                    self.canvas.scene().removeItem(item)

    def clear_rubberbands(self):
                """ Removes rubberband objects from the map canvas """
                for item in self.canvas.scene().items():
                    if isinstance(item, QgsRubberBand):
                        self.canvas.scene().removeItem(item) 