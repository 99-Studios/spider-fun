import sys
import os
import random
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtGui import QPixmap, QTransform, QCursor # Add QCursor here
from PyQt6.QtCore import Qt, QTimer, QPoint

class FunSpider(QMainWindow):
    def __init__(self):
        super().__init__()

        self.version = "1.1.0"

        # Window Setup
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
        self.img_stare = self.load_image("stare.png")
        self.img_sleep = self.load_image("sleep.png")
        self.img_read = self.load_image("read.png")

        self.label = QLabel(self)
        self.label.setFixedSize(self.window_w, self.window_h)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setPixmap(self.img_idle)
        self.resize(self.window_w, self.window_h)

        # 3. BRAIN & MOVEMENT
        self.state = "WALKING" 
        self.state_timer = 0    
        self.is_dragging = False
        self.walk_timer = 0
        self.last_mouse_pos = QPoint()

        # Initial Position (Primary Screen Floor)
        screen = QApplication.primaryScreen().geometry()
        self.move(100, screen.height() - self.window_h)

        # Heartbeat Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_behavior)
        self.timer.start(30) 

    def load_image(self, name):
        # Compatibility for PyInstaller (Finding assets in EXE mode)
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_path, "assets", name)
        if os.path.exists(path):
            return QPixmap(path).scaledToHeight(self.scale_height, Qt.TransformationMode.SmoothTransformation)
        return QPixmap()

    def get_current_screen_geometry(self):
        # Finds the geometry of the monitor the spider is currently on
        return self.screen().geometry()

    def get_flipped_pixmap(self, pixmap):
        if self.direction == -1:
            return pixmap.transformed(QTransform().scale(-1, 1))
        return pixmap

    def update_behavior(self):
        if self.is_dragging: return 

        screen_geo = self.get_current_screen_geometry()
        floor_y = screen_geo.top() + screen_geo.height() - self.window_h
        curr_x, curr_y = self.pos().x(), self.pos().y()

        if curr_y < floor_y or abs(self.vel_x) > 0.5:
            self.apply_physics(curr_x, curr_y, screen_geo, floor_y)
            return

        # --- THE BRAIN LOGIC ---
        self.state_timer -= 1
        if self.state_timer <= 0:
            choice = random.random()
            if choice < 0.4: # 40% Walk
                self.state = "WALKING"
                self.state_timer = random.randint(60, 200)
            elif choice < 0.55: # 15% Idle
                self.state = "IDLE"
                self.state_timer = random.randint(30, 100)
            elif choice < 0.7: # 15% Stare
                self.state = "STARE"
                self.state_timer = random.randint(60, 120)
            elif choice < 0.8: # 10% Sleep
                self.state = "SLEEP"
                self.state_timer = random.randint(200, 500)
            elif choice < 0.9: # 10% Follow Mouse
                self.state = "FOLLOWING"
                self.state_timer = random.randint(100, 250)
            else: # 10% Reading
                self.state = "READING"
                self.state_timer = random.randint(150, 300)

        # Execute States
        if self.state == "READING":
            self.label.setPixmap(self.get_flipped_pixmap(self.img_read))
            # Optional: Tiny 1-pixel jitters to look like he's scanning lines
            if random.random() < 0.1:
                offset = random.choice([-1, 0, 1])
                self.move(curr_x + offset, curr_y)

        elif self.state == "FOLLOWING":
            # 1. Find the mouse using QCursor (much more stable)
            mouse_pos = QCursor.pos()
            mouse_x = mouse_pos.x()
            
            # 2. Determine direction
            spider_center_x = curr_x + (self.window_w // 2)
            
            if abs(mouse_x - spider_center_x) > 20:
                self.direction = 1 if mouse_x > spider_center_x else -1
                self.walk_logic(curr_x, screen_geo, floor_y)
            else:
                # He's close enough!
                self.label.setPixmap(self.get_flipped_pixmap(self.img_idle))

        elif self.state == "WALKING":
            if random.random() < 0.01: self.direction *= -1
            self.walk_logic(curr_x, screen_geo, floor_y)
        # ... rest of idle/stare/sleep states ...
        elif self.state == "IDLE":
            self.label.setPixmap(self.get_flipped_pixmap(self.img_idle))
        elif self.state == "STARE":
            self.label.setPixmap(self.img_stare)
        elif self.state == "SLEEP":
            self.label.setPixmap(self.get_flipped_pixmap(self.img_sleep))

    def walk_logic(self, curr_x, screen_geo, floor_y):
        new_x = curr_x + (self.walk_speed * self.direction)
        
        self.walk_timer += 1
        current_pix = self.img_walk1 if self.walk_timer % 16 < 8 else self.img_walk2
        self.label.setPixmap(self.get_flipped_pixmap(current_pix))

        # Edge Detection (Monitor specific)
        if new_x > screen_geo.left() + screen_geo.width() - self.window_w or new_x < screen_geo.left():
            self.direction *= -1
            new_x = curr_x
        
        self.move(new_x, floor_y)

    def apply_physics(self, curr_x, curr_y, screen_geo, floor_y):
        self.label.setPixmap(self.get_flipped_pixmap(self.img_pickup))
        self.vel_y += self.gravity
        self.vel_x *= self.friction
        
        new_x = int(curr_x + self.vel_x)
        new_y = int(curr_y + self.vel_y)

        # Wall Bouncing (Monitor specific)
        if new_x < screen_geo.left() or new_x > screen_geo.left() + screen_geo.width() - self.window_w:
            self.vel_x *= -0.5 
            new_x = curr_x

        # Floor Landing
        if new_y >= floor_y:
            new_y = floor_y
            self.vel_y = 0
            if abs(self.vel_x) < 0.5: 
                self.vel_x = 0 
                self.state = "IDLE" 
                self.state_timer = 20

        self.move(new_x, new_y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.state = "IDLE"
            self.label.setPixmap(self.img_pickup)
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            self.last_mouse_pos = event.globalPosition().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            QApplication.quit()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            now = event.globalPosition().toPoint()
            # Calculate throw velocity
            self.vel_x = (now.x() - self.last_mouse_pos.x()) * 0.5
            self.vel_y = (now.y() - self.last_mouse_pos.y()) * 0.5
            self.last_mouse_pos = now
            self.move(now - self.drag_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            # Update walking direction based on horizontal velocity
            if self.vel_x > 0: self.direction = 1
            elif self.vel_x < 0: self.direction = -1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    spider = FunSpider()
    spider.show()
    sys.exit(app.exec())