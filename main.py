import sys
import os
import random # Added for decision making
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtCore import Qt, QTimer, QPoint

class FunSpider(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    # 1. SETTINGS
        self.scale_height = 80  
        self.window_w = 180 
        self.window_h = 100
        self.walk_speed = 3
        self.direction = 1 
        
        self.gravity = 0.8
        self.friction = 0.90
        self.vel_x = 0          
        self.vel_y = 0          
        
    # 2. LOAD IMAGES
        self.img_idle = self.load_image("idle.png")
        self.img_walk1 = self.load_image("walk_1.png")
        self.img_walk2 = self.load_image("walk_2.png")
        self.img_pickup = self.load_image("pickup.png")
        self.img_stare = self.load_image("stare.png") # Make sure this exists in assets!

        self.label = QLabel(self)
        self.label.setFixedSize(self.window_w, self.window_h)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setPixmap(self.img_idle)
        self.resize(self.window_w, self.window_h)

    # 3. BRAIN STATES
        self.state = "WALKING" # Initial state
        self.state_timer = 0    # How long to stay in a state

        screen_geo = QApplication.primaryScreen().geometry()
        self.floor_y = screen_geo.height() - self.window_h
        self.move(100, self.floor_y)

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

        # Physics check (If thrown/falling)
        if curr_y < self.floor_y or abs(self.vel_x) > 0.5:
            self.apply_physics(curr_x, curr_y)
            return

        # --- THE BRAIN LOGIC ---
        self.state_timer -= 1
        
        if self.state_timer <= 0:
            # Pick a new random state
            # 70% chance to walk, 20% to idle, 10% to stare
            choice = random.random()
            if choice < 0.7:
                self.state = "WALKING"
                self.state_timer = random.randint(50, 150) # Walk for 1.5 to 4.5 seconds
            elif choice < 0.9:
                self.state = "IDLE"
                self.state_timer = random.randint(30, 80)
            else:
                self.state = "STARE"
                self.state_timer = random.randint(40, 100)

        # Execute the current state
        if self.state == "WALKING":
            self.walk_logic(curr_x)
        elif self.state == "IDLE":
            self.label.setPixmap(self.get_flipped_pixmap(self.img_idle))
        elif self.state == "STARE":
            self.label.setPixmap(self.img_stare) # He looks directly at you!

    def walk_logic(self, curr_x):
        new_x = curr_x + (self.walk_speed * self.direction)
        screen_width = QApplication.primaryScreen().geometry().width()
        
        self.walk_timer += 1
        if self.walk_timer % 16 < 8:
            current_pix = self.img_walk1
        else:
            current_pix = self.img_walk2
            
        self.label.setPixmap(self.get_flipped_pixmap(current_pix))

        if new_x > screen_width - self.window_w or new_x < 0:
            self.direction *= -1
        
        self.move(new_x, self.floor_y)

    def apply_physics(self, curr_x, curr_y):
        self.label.setPixmap(self.get_flipped_pixmap(self.img_pickup))
        self.vel_y += self.gravity
        self.vel_x *= self.friction
        
        new_x = int(curr_x + self.vel_x)
        new_y = int(curr_y + self.vel_y)

        screen_width = QApplication.primaryScreen().geometry().width()
        if new_x < 0 or new_x > screen_width - self.window_w:
            self.vel_x *= -0.5 
            new_x = curr_x

        if new_y >= self.floor_y:
            new_y = self.floor_y
            self.vel_y = 0
            if abs(self.vel_x) < 0.5: 
                self.vel_x = 0 
                self.state = "IDLE" # Switch to idle after landing

        self.move(new_x, new_y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.label.setPixmap(self.img_pickup)
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            self.last_mouse_pos = event.globalPosition().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            QApplication.quit()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            now = event.globalPosition().toPoint()
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