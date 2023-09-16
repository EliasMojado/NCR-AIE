from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGraphicsDropShadowEffect, QLabel
from PyQt5.QtGui import QColor, QPalette, QFont, QImage, QPixmap
from PyQt5.QtCore import Qt, QRect, QTimer
import sys

import cv2
import numpy as np
from tensorflow.keras.models import load_model
from interface import Box
import mediapipe as mp

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

#---------------------------------------AKO NI DIRI ---------------------------------------------------------------------------------------------#

# Mediapipe drawing and model objects
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_holistic = mp.solutions.holistic
mp_hands = mp.solutions.hands

# Functions
def extract_keypoints(results):
    lh = np.array([[res.x, res.y, res.z, res.visibility] for res in results.multi_hand_landmarks[0].landmark]).flatten() if results.multi_hand_landmarks else np.zeros(21*4)
    rh = np.array([[res.x, res.y, res.z, res.visibility] for res in results.multi_hand_landmarks[1].landmark]).flatten() if results.multi_hand_landmarks and len(results.multi_hand_landmarks) > 1 else np.zeros(21*4)
    return np.concatenate([lh, rh])

def draw_styled_landmarks(image, results):
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image, results

class ARbox(Box):
    def __init__(self, x, y, width, height, title, parent=None):
        super(ARbox, self).__init__(x, y, width, height, title, parent)
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(1)
        
        # Load the trained models
        self.models = []
        self.actions = ["navigate", "inserting", "type"]
        for action in self.actions:
            model = load_model(f"{action}_model.h5")
            self.models.append(model)
        
        # Set default active model
        self.active_model_index = 1
        
        # Initialize sequence and max_length
        self.sequence = []
        self.max_length = 60
        
        # Initialize Mediapipe Hands for detection
        self.mp_hands = mp.solutions.hands
        self.hands = mp.solutions.hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        # Initialize QTimer for updating the video feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 ms
        
        # Create QLabel for video display
        self.video_label = QLabel(self)
        self.video_label.setGeometry(0, 0, width // 2, height)  # Take up 50% of the entire box
        
        # Create QLabel for text display
        self.text_label = QLabel(self)
        self.text_label.setGeometry(width // 2, 0, width // 2, height)
        self.text_label.setAlignment(Qt.AlignTop)
        
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Make detections
            image, results = mediapipe_detection(frame, self.hands)
            
            # Draw landmarks
            draw_styled_landmarks(image, results)
            
            # Extract keypoints
            keypoints = extract_keypoints(results)
            self.sequence.append(keypoints)
            
            # If sequence length is more than max_length, remove the earliest frame
            if len(self.sequence) > self.max_length:
                self.sequence.pop(0)
            
            self.sequence = self.sequence[-self.max_length:]
            
            # Make prediction if we have enough frames
            if len(self.sequence) == self.max_length:
                sequence_array = np.array([self.sequence])
                
                prediction = self.models[self.active_model_index].predict(sequence_array)
                confidence = prediction[0][0]
                
                if confidence < 0.9:
                    predicted_action = 'Unknown'
                else:
                    predicted_action = self.actions[self.active_model_index]
                
                # Update text information
                self.text_label.setText(f"Active Model: {self.actions[self.active_model_index]}\nPredicted Action: {predicted_action}\nProbability: {confidence:.2f}")
            
            # Convert the frame to QImage and display it
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qt_image))

#---------------------------------------AKO NI DIRI ---------------------------------------------------------------------------------------------#

# Main window class
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Set window title
        self.setWindowTitle("NCR AI Ensemble")
        
        # Set window size
        self.setGeometry(100, 100, 800, 600)
        
        # Set background color to #4C4C4C
        palette = self.palette()
        palette.setColor(QPalette.Background, QColor("#2D2D2D"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Add Box widgets to the main window
        self.box = Box(50, 50, 700, 800, "Action Recognition",self)
        self.box = Box(800, 50, 900, 500, "Skimming Device Recognition",self)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
