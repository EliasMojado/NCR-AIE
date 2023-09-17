import cv2
from PyQt5.QtWidgets import QLabel, QGraphicsView, QGraphicsScene, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QIcon
import os
import numpy as np
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QPushButton

def histogram_equalization(image):
    equalized_image = cv2.equalizeHist(image)
    return equalized_image


def local_contrast_normalization(image):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    normalized_image = clahe.apply(image)
    return normalized_image


def mse(imageA, imageB):
    # image_a_h = histogram_equalization(imageA)
    # image_b_h = histogram_equalization(imageB)
    
    image_a_final = histogram_equalization(imageA)
    image_b_final = histogram_equalization(imageB)
    
    # image_a_final = imageA
    # image_b_final = imageB
    """Compute the Mean Squared Error between two images."""
    err = np.sum((image_a_final.astype("float") - image_b_final.astype("float")) ** 2)
    err /= float(image_a_final.shape[0] * image_b_final.shape[1])
    return err

def start_realtime_camera(qtimer, graphics_view, graphics_scene, mse_label, reference_image_path, crop_parameters, frame_skip=30):
    cap = cv2.VideoCapture(0)  # Open the default camera (usually the webcam)
    frame_count = 0
    total_mse = 0
    # Load and crop the reference image
    reference_image = cv2.imread(reference_image_path)
    x, y, width, height = crop_parameters
    reference_image = reference_image[y:y + height, x:x + width]
    reference_image = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)

    def update_frame():
        nonlocal frame_count, total_mse
        ret, frame = cap.read()
        if not ret:
            return

        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
        
        if frame_count % frame_skip == 0:
            cropped_frame = frame[y:y + height, x:x + width]
            gray_cropped_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
            
            mse_value = mse(reference_image, gray_cropped_frame)
            total_mse += mse_value
            average_mse = total_mse / (frame_count // frame_skip + 1)
            mse_label.setText(f"Average MSE: {average_mse:.2f}")

        frame_count += 1

        # Convert the image from OpenCV BGR format to RGB
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        graphics_scene.clear()
        graphics_scene.addPixmap(pixmap)
        graphics_view.setScene(graphics_scene)

    def start_camera():
        qtimer.timeout.connect(update_frame)
        cap.open(0)
        
    def stop_camera():
        qtimer.timeout.disconnect(update_frame)
        cap.release()

    return start_camera, stop_camera


    

def addSkimmingDetails(main_window, box):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    timer1 = QTimer(main_window)
    timer2 = QTimer(main_window)
    # Create the absolute path by combining the current directory and the relative path
    absolute_image_path = os.path.join(current_directory, "skim", "captured_image.jpg")
    
    
    # Initialize the first QGraphicsView to display camera feed on the left side
    camera_view1 = QGraphicsView(box)
    camera_view1.setGeometry(20, 60, 470, 300)  # Set position and size
    camera_view1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    # Initialize the second QGraphicsView to display camera feed on the right side
    camera_view2 = QGraphicsView(box)
    camera_view2.setGeometry(550, 60, 470, 300)  # Set position and size
    camera_view2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


    # Add QLabel for displaying average MSE for left view
    avg_mse_label_left = QLabel("Average MSE Left: N/A", box)
    avg_mse_label_left.setGeometry(20, 450, 400, 40)
    avg_mse_label_left.setFont(QFont("Arial", 20))
    # avg_mse_label_left.setPalette(QPalette().setColor(QPalette.WindowText, QColor("white")))
    
    # Add QLabel for displaying average MSE for right view
    avg_mse_label_right = QLabel("Average MSE Right: N/A", box)
    avg_mse_label_right.setGeometry(550, 450, 400, 40)
    avg_mse_label_right.setFont(QFont("Arial", 20))
    # avg_mse_label_right.setPalette(QPalette().setColor(QPalette.WindowText, QColor("white")))

    palette = QPalette()
    palette.setColor(QPalette.WindowText, QColor("white"))
    avg_mse_label_left.setPalette(palette)
    avg_mse_label_right.setPalette(palette)      
    # Initialize QGraphicsScene to hold QImage
    scene1 = QGraphicsScene()
    scene2 = QGraphicsScene()
    camera_view1.setScene(scene1)
    camera_view2.setScene(scene2)
    

    crop_parameters = (449, 134, 105, 124)
    
    # Initialize the camera for left and right views
    start_camera1, stop_camera1 = start_realtime_camera(timer1, camera_view1, scene1, avg_mse_label_left, absolute_image_path, crop_parameters)
    start_camera2, stop_camera2 = start_realtime_camera(timer2, camera_view2, scene2, avg_mse_label_right, absolute_image_path, crop_parameters)

    # Add Start and Stop buttons for the left camera
    start_button_left = QPushButton("Start Camera Left", box)
    start_button_left.setGeometry(20, 400, 200, 40)
    start_button_left.clicked.connect(start_camera1)
    stop_button_left = QPushButton("Stop Camera Left", box)
    stop_button_left.setGeometry(250, 400, 200, 40)
    stop_button_left.clicked.connect(stop_camera1)

    # Add Start and Stop buttons for the right camera
    start_button_right = QPushButton("Start Camera Right", box)
    start_button_right.setGeometry(550, 400, 200, 40)
    start_button_right.clicked.connect(start_camera2)
    stop_button_right = QPushButton("Stop Camera Right", box)
    stop_button_right.setGeometry(780, 400, 200, 40)
    stop_button_right.clicked.connect(stop_camera2)
    
    timer1.start(50)  # 30 ms between each frame, change as needed
    timer2.start(50)  # 30 ms between each frame, change as needed