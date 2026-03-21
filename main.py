import sys
import os
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize

class FunSpider(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. Window Configuration
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 2. Set a consistent size for your spider
        # You can change 150, 150 to be bigger or smaller!
        self.pet_width = 150
        self.pet_height = 150

        # 3. Add the Image
        self.label = QLabel(self)
        image_path = os.path.join("assets", "idle.png")
        
        if os.path.exists(image_path):
            # Load the image
            full_pixmap = QPixmap(image_path)
            
            # SCALE the image to fit our pet_width and pet_height
            scaled_pixmap = full_pixmap.scaled(
                self.pet_width, 
                self.pet_height, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.label.setPixmap(scaled_pixmap)
            self.label.adjustSize() # Wrap the label tightly around the scaled image
            
            # Resize the actual window to match the scaled image
            self.resize(self.pet_width, self.pet_height)
        else:
            print(f"Error: Could not find {image_path}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    spider = FunSpider()
    spider.show()
    sys.exit(app.exec())