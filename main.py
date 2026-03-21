import sys
import os
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class FunSpider(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. Window Configuration
        # FramelessWindowHint: Removes the title bar and exit buttons
        # WindowStaysOnTopHint: Keeps the spider above all other windows
        # Tool: Hides the icon from the taskbar so it feels like a real pet
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        
        # Makes the window background invisible
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 2. Add the Image (The "Label")
        self.label = QLabel(self)
        
        # Path to your idle image
        # Note: 'assets/idle.png' assumes your folder structure is correct!
        image_path = os.path.join("assets", "idle.png")
        
        if os.path.exists(image_path):
            self.pixmap = QPixmap(image_path)
            self.label.setPixmap(self.pixmap)
            # Resize the window to match the image size
            self.resize(self.pixmap.width(), self.pixmap.height())
        else:
            print(f"Error: Could not find {image_path}. Check your folder!")

    def mousePressEvent(self, event):
        """Allows you to close the pet by right-clicking it (for testing!)"""
        if event.button() == Qt.MouseButton.RightButton:
            QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    spider = FunSpider()
    spider.show()
    sys.exit(app.exec())