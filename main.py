import sys
import os
import random
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtCore import Qt, QTimer, QPoint

class FunSpider(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. Window Flag Setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 2. Dimensions & Physics Settings
        self.scale_height = 80  
        self.hang_height = 180 
        self.window_w = 180 
        self.window_h = 100
        self.walk_speed = 3
        self.direction = 1 
        self.gravity = 0.8
        self.friction = 0.90
        self.vel_x = 0          
        self.vel_y = 0          
        self.ceiling_threshold = 80 # How close to top to "stick"

        # 3. Load All Images
        self.img_idle = self.load_image("idle.png", self.scale_height)
        self.img_walk1 = self.load_image("walk_1.png", self.scale_height)
        self.img_walk2 = self.load_image("walk_2.png", self.scale_height)
        self.img_pickup = self.load_image("pickup.png", self.scale_height)
        self.img_stare = self.load_image("stare.png", self.scale_height)
        self.img_sleep = self.load_image("sleep.png", self.scale_height)
        self.img_hang = self.load_image("hang.png", self.hang_height)

        # 4. GUI Elements
        self.label = QLabel(self)
        self.label.setFixedSize(self.window_w, self.hang_height + 20) # Max height room
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setPixmap(self.img_idle)
        self.resize(self.window_w, self.window_h)

        # 5. State Machine
        self.state = "WALKING" 
        self.state_timer = 0    
        self.is_dragging = False
        self.walk_timer = 0
        
        # 6. Positioning
        screen_geo = QApplication.primaryScreen().geometry()
        self.floor_y = screen_geo.height() - self.window_h
        self.move(100, self.floor_y)

        # 7. Main Heartbeat Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_behavior)
        self.timer.start(30) 

    def load_image(self, name, height):
        path = os.path.join("assets", name)
        if os.path.exists(path):
            pix = QPixmap(path)
            return pix.scaledToHeight(height, Qt.TransformationMode.SmoothTransformation)
        return QPixmap()

    def get_flipped_pixmap(self, pixmap):
        if self.direction == -1:
            return pixmap.transformed(QTransform().scale(-1, 1))
        return pixmap

    def update_behavior(self):
        if self.is_dragging: return 

        curr_x, curr_y = self.pos().x(), self.pos().y()

        # Logic for Hanging
        if self.state == "HANGING":
            if self.height() != self.hang_height + 20:
                self.resize(self.window_w, self.hang_height + 20)
            self.label.setPixmap(self.img_hang)
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.state = "IDLE"
                self.resize(self.window_w, self.window_h)
            return

        # Logic for Physics (Jumping/Falling/Thrown)
        if curr_y < self.floor_y or abs(self.vel_x) > 0.5 or abs(self.vel_y) > 0.5:
            self.apply_physics(curr_x, curr_y)
            return

        # Brain / Decision Making
        self.state_timer -= 1
        if self.state_timer <= 0:
            choice = random.random()
            if choice < 0.5:
                self.state = "WALKING"; self.state_timer = random.randint(60, 200)
            elif choice < 0.7:
                self.state = "IDLE"; self.state_timer = random.randint(30, 100)
            elif choice < 0.85:
                self.state = "STARE"; self.state_timer = random.randint(60, 120)
            elif choice < 0.94:
                self.state = "SLEEP"; self.state_timer = random.randint(200, 500)
            else:
                self.state = "JUMPING"; self.vel_y = -35 # Big Jump

        # Execute Non-Physics States
        if self.state == "WALKING":
            if random.random() < 0.01: self.direction *= -1
            self.walk_logic(curr_x)
        elif self.state == "IDLE":
            self.label.setPixmap(self.get_flipped_pixmap(self.img_idle))
        elif self.state == "STARE":
            self.label.setPixmap(self.img_stare)
        elif self.state == "SLEEP":
            self.label.setPixmap(self.get_flipped_pixmap(self.img_sleep))

    def walk_logic(self, curr_x):
        new_x = curr_x + (self.walk_speed * self.direction)
        screen_w = QApplication.primaryScreen().geometry().width()
        self.walk_timer += 1
        img = self.img_walk1 if self.walk_timer % 16 < 8 else self.img_walk2
        self.label.setPixmap(self.get_flipped_pixmap(img))
        if new_x > screen_w - self.window_w or new_x < 0: self.direction *= -1
        self.move(new_x, self.floor_y)

    def apply_physics(self, curr_x, curr_y):
        self.vel_y += self.gravity
        self.vel_x *= self.friction
        new_x, new_y = int(curr_x + self.vel_x), int(curr_y + self.vel_y)

        # Ceiling Check
        if new_y <= self.ceiling_threshold and self.vel_y < 0:
            self.move(new_x, 0); self.vel_y = 0; self.vel_x = 0
            self.state = "HANGING"; self.state_timer = random.randint(150, 400)
            return

        # Wall/Floor Check
        screen_w = QApplication.primaryScreen().geometry().width()
        if new_x < 0 or new_x > screen_w - self.window_w: self.vel_x *= -0.5; new_x = curr_x
        if new_y >= self.floor_y:
            new_y = self.floor_y; self.vel_y = 0
            if abs(self.vel_x) < 0.5: self.vel_x = 0; self.state = "IDLE"
            self.resize(self.window_w, self.window_h)
        self.move(new_x, new_y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True; self.state = "IDLE"
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