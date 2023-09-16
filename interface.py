from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGraphicsDropShadowEffect, QLabel
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtCore import Qt, QRect
import sys
from skimming import addSkimmingDetails

# Parent class 'Box'
class Box(QWidget):
    def __init__(self, x, y, width, height, title, parent=None):
        super(Box, self).__init__(parent)
        self.setGeometry(QRect(x, y, width, height))
        
        # Set background color to #2D2D2D
        palette = self.palette()
        palette.setColor(QPalette.Background, QColor("#4C4C4C"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

         # Add shadow effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(50)  # Set the blur radius
        self.shadow.setColor(QColor(0, 0, 0, 160))  # Set the shadow color
        self.shadow.setOffset(0, 10)  # Set the shadow offset
        self.setGraphicsEffect(self.shadow)

        # Add title
        self.title = QLabel(title, self)
        self.title.move(20, 30)  # Position at top-left corner
        
        # Set font and size
        font = QFont("Arial", 12)
        self.title.setFont(font)

        # Set text color to white
        title_palette = QPalette()
        title_palette.setColor(QPalette.WindowText, QColor("white"))
        self.title.setPalette(title_palette)

# Main window class
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Set window title
        self.setWindowTitle("NCR AI ensemble")
        
        # Set window size
        self.setGeometry(100, 100, 800, 600)
        
        # Set background color to #4C4C4C
        palette = self.palette()
        palette.setColor(QPalette.Background, QColor("#2D2D2D"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Add Box widgets to the main window
        self.box_action_recognition = Box(50, 50, 700, 800, "Action Recognition", self)
        self.box_skimming_device = Box(800, 50, 900, 500, "Skimming Device Recognition", self)
        addSkimmingDetails(self, self.box_skimming_device)

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
