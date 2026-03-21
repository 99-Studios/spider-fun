import sys
import os
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtCore import Qt, QTimer, QPoint

class FunSpider(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 1. Settings
        self.scale_height = 80  
        self.window_size = 180  
        self.speed = 8 
        self.direction = 1 
        
        # 2. Load Images
        self.img_idle = self.load_image("idle.png")
        self.img_walk1 = self.load_image("walk_1.png")
        self.img_walk2 = self.load_image("walk_2.png")
        self.img_pickup = self.load_image("pickup.png")

        self.label = QLabel(self)
        self.label.setFixedSize(self.window_size, self.window_size)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setPixmap(self.img_idle)
        self.resize(self.window_size, self.window_size)

        # 3. FIX: CALCULATE TRUE BOTTOM
        # 'screen().geometry()' includes the taskbar area
        screen_geo = QApplication.primaryScreen().geometry()
        
        # We want the bottom of the spider's box to hit the bottom of the screen.
        # If he still looks like he's "floating," decrease the '10' or '20' offset.
        self.floor_y = screen_geo.height() - self.window_size + 30 # Added +30 to push him lower
        
        self.move(100, self.floor_y)

        self.is_dragging = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_behavior)
        self.timer.start(100)
        self.walk_frame = 0

    def load_image(self, name):
        path = os.path.join("assets", name)
        if os.path.exists(path):
            pix = QPixmap(path)
            return pix.scaledToHeight(self.scale_height, Qt.TransformationMode.SmoothTransformation)
        return QPixmap()

    def get_flipped_pixmap(self, pixmap):
        if self.direction == -1:
            return pixmap.transformed(QTransform().scale(-1, 1))
        return pixmap

    def update_behavior(self):
        if self.is_dragging:
            return 

        current_pos = self.pos()
        new_x = current_pos.x() + (self.speed * self.direction)
        screen_width = QApplication.primaryScreen().geometry().width()
        
        # Animation logic
        if self.walk_frame == 0:
            current_pix = self.img_walk1
            self.walk_frame = 1
        else:
            current_pix = self.img_walk2
            self.walk_frame = 0
            
        self.label.setPixmap(self.get_flipped_pixmap(current_pix))

        # Boundary check
        if new_x > screen_width - self.window_size or new_x < 0:
            self.direction *= -1
        
        # Re-apply floor_y every frame to ensure he stays stuck to the bottom
        self.move(new_x, self.floor_y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.label.setPixmap(self.img_pickup)
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            QApplication.quit()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            # When let go, he returns to the floor height
            self.move(self.pos().x(), self.floor_y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    spider = FunSpider()
    spider.show()
    sys.exit(app.exec())