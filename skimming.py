import cv2
from PyQt5.QtWidgets import QLabel, QGraphicsView, QGraphicsScene, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QIcon
import os
import numpy as np
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import QRect
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

def start_realtime_camera(qtimer, graphics_view, graphics_scene, mse_label , reference_image_path, crop_parameters, frame_skip=30):
    cap = cv2.VideoCapture(0)  # Open the default camera (usually the webcam)
    frame_count = 0
    
    # Load and crop the reference image
    reference_image = cv2.imread(reference_image_path)
    x, y, width, height = crop_parameters
    reference_image = reference_image[y:y + height, x:x + width]
    reference_image = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)

    def update_frame():
        nonlocal frame_count
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            return

        if frame_count % frame_skip == 0:
            cropped_frame = frame[y:y + height, x:x + width]
            gray_cropped_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
            mse_value = mse(reference_image, gray_cropped_frame)
            mse_label.setText(f"Difference (MSE) between reference image and frame_{frame_count}: {mse_value:.2f}")

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

    qtimer.timeout.connect(update_frame)
    

def addSkimmingDetails(main_window, box):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    timer = QTimer(main_window)
    # Create the absolute path by combining the current directory and the relative path
    absolute_image_path = os.path.join(current_directory, "skim", "captured_image.jpg")
    
    # Initialize QLabel as an image placeholder on the left side
    image_placeholder = QLabel(box)
    image_placeholder.setGeometry(20, 60, 400, 300)  # Set position and size
    
    # Create a QPixmap object and load the image from the absolute path
    pixmap = QPixmap(absolute_image_path)

    if pixmap.isNull():
        print("Failed to load image!")
    else:
        # Crop the image starting from the right
        crop_x = pixmap.width() - 400  # Adjust the value as needed
        crop_y = 0
        crop_width = 400  # Adjust the value as needed
        crop_height = 300  # Adjust the value as needed
        cropped_pixmap = pixmap.copy(QRect(crop_x, crop_y, crop_width, crop_height))
        
        image_placeholder.setPixmap(cropped_pixmap)
        print("Image loaded and cropped successfully.")
        
    # Initialize QGraphicsView to display camera feed on the right side
    camera_view = QGraphicsView(box)
    camera_view.setGeometry(430, 60, 400, 300)  # Set position and size
    camera_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

   # Add QLabel for displaying MSE
    mse_label = QLabel("MSE: N/A", box)
    mse_label.setGeometry(20, 370, 800, 40)  # Set position and size

    # Set the font size
    font = QFont("Arial", 16)  # The first parameter is the font family, and the second is the font size.
    mse_label.setFont(font)
    
    # Set the font color to green
    palette = QPalette()
    palette.setColor(QPalette.WindowText, QColor("green"))
    mse_label.setPalette(palette)
       
    # Initialize QGraphicsScene to hold QImage
    scene = QGraphicsScene()
    camera_view.setScene(scene)
    
    crop_parameters = (452, 132, 100, 127)
    start_realtime_camera(timer, camera_view, scene, mse_label, absolute_image_path, crop_parameters)
    timer.start(30)  # 30 ms between each frame, change as needed
