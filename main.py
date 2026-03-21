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

    # 1. TUNED SETTINGS (Slower & Smaller Box)
        self.scale_height = 80  
        self.window_size_h = 100  # Height of the window is now closer to spider height
        self.window_size_w = 180  # Width of the window
        self.walk_speed = 3       # Much slower walk
        self.direction = 1 
        
        self.gravity = 0.8        # Very gentle falling
        self.friction = 0.90      # Slows down quickly after a throw
        
        self.vel_x = 0          
        self.vel_y = 0          
        
    # 2. Load Images
        self.img_idle = self.load_image("idle.png")
        self.img_walk1 = self.load_image("walk_1.png")
        self.img_walk2 = self.load_image("walk_2.png")
        self.img_pickup = self.load_image("pickup.png")

        self.label = QLabel(self)
        self.label.setFixedSize(self.window_size_w, self.window_size_h)
        # Center the spider in this smaller box
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setPixmap(self.img_idle)
        self.resize(self.window_size_w, self.window_size_h)

    # 3. Position (Calculate floor based on new smaller height)
        screen_geo = QApplication.primaryScreen().geometry()
        self.floor_y = screen_geo.height() - self.window_size_h
        self.move(100, self.floor_y)

    # 4. Timer
        self.is_dragging = False
        self.last_mouse_pos = QPoint()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_behavior)
        self.timer.start(30) 
        self.walk_timer = 0

    def load_image(self, name):
        path = os.path.join("assets", name)
        if os.path.exists(path):
            return QPixmap(path).scaledToHeight(self.scale_height, Qt.TransformationMode.SmoothTransformation)
        return QPixmap()

    def get_flipped_pixmap(self, pixmap):
        if self.direction == -1:
            return pixmap.transformed(QTransform().scale(-1, 1))
        return pixmap

    def update_behavior(self):
        if self.is_dragging:
            return 

        curr_x, curr_y = self.pos().x(), self.pos().y()

        if curr_y < self.floor_y or abs(self.vel_x) > 0.5:
            self.apply_physics(curr_x, curr_y)
        else:
            self.walk_logic(curr_x)

    def walk_logic(self, curr_x):
        self.vel_y = 0
        self.vel_x = 0
        
        new_x = curr_x + (self.walk_speed * self.direction)
        screen_width = QApplication.primaryScreen().geometry().width()
        
        # Slow down animation cycle
        self.walk_timer += 1
        if self.walk_timer % 16 < 8: # Frame stays for 8 ticks
            current_pix = self.img_walk1
        else:
            current_pix = self.img_walk2
            
        self.label.setPixmap(self.get_flipped_pixmap(current_pix))

        if new_x > screen_width - self.window_size_w or new_x < 0:
            self.direction *= -1
        
        self.move(new_x, self.floor_y)

    def apply_physics(self, curr_x, curr_y):
        self.label.setPixmap(self.get_flipped_pixmap(self.img_pickup))
        self.vel_y += self.gravity
        self.vel_x *= self.friction
        
        # Lowered max speed for safety
        max_speed = 15
        self.vel_x = max(-max_speed, min(max_speed, self.vel_x))
        self.vel_y = max(-max_speed, min(max_speed, self.vel_y))

        new_x = int(curr_x + self.vel_x)
        new_y = int(curr_y + self.vel_y)

        screen_width = QApplication.primaryScreen().geometry().width()
        if new_x < 0 or new_x > screen_width - self.window_size_w:
            self.vel_x *= -0.5 
            new_x = curr_x

        if new_y >= self.floor_y:
            new_y = self.floor_y
            self.vel_y = 0
            if abs(self.vel_x) < 0.5: self.vel_x = 0 

        self.move(new_x, new_y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            # Re-center logic is cleaner with smaller window
            self.label.setPixmap(self.img_pickup)
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            self.last_mouse_pos = event.globalPosition().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            QApplication.quit()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            now = event.globalPosition().toPoint()
            # Gentler throw calculation
            self.vel_x = (now.x() - self.last_mouse_pos.x()) * 0.5
            self.vel_y = (now.y() - self.last_mouse_pos.y()) * 0.5
            self.last_mouse_pos = now
            self.move(now - self.drag_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            if self.vel_x > 0: self.direction = 1
            elif self.vel_x < 0: self.direction = -1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    spider = FunSpider()
    spider.show()
    sys.exit(app.exec())