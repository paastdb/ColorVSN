import cv2
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget, QHBoxLayout, QMessageBox, \
    QFrame, QFileDialog
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont
import resources_rc


class ColorMapDialog(QDialog):
    def __init__(self, parent=None):
        super(ColorMapDialog, self).__init__(parent)
        self.setWindowTitle("Select Color Map")
        self.setWindowIcon(QIcon(":/icons/icons/color-palette-bars-icon.png"))

        # Remove the question mark/help button from the title bar
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Set the custom color for the title bar using style sheet
        self.setStyleSheet("QDialog::title { background-color: #FFF9C9; }"  # Adjust the color as desired
                           "QDialog { background-color: white; }")  # Adjust the color as desired

        self.setFixedSize(500, 400)
        self.layout = QVBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        self.scroll_content = QWidget()
        self.scroll_area.setWidget(self.scroll_content)

        self.scroll_content.setStyleSheet("background:white")

        self.scroll_area.setStyleSheet("""
        QScrollArea{border:none; background:white}
        QScrollBar:vertical {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #CACACA, stop:0.25 #FFE826,
                                stop:0.5 #030FFF, stop:1 #AC0000);
}

/* Style for vertical scroll bar */
QScrollBar:vertical {
    border: none;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #CACACA, stop:0.25 #FFE826,
                                stop:0.5 #030FFF, stop:1 #AC0000);
    width: 12px; /* Adjust width as needed */
    margin: 0px 0px 0px 0px;
    border-radius:2px
}

/* Style for horizontal scroll bar */
QScrollBar:horizontal {
    border: none;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #CACACA, stop:0.25 #FFE826,
                                stop:0.5 #030FFF, stop:1 #AC0000);
    height: 10px; /* Adjust height as needed */
    margin: 0px 0px 0px 0px;
}

/* Style for scroll bar handle */
QScrollBar::handle {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #CACACA, stop:0.25 #FFE826,
                                stop:0.5 #030FFF, stop:1 #AC0000); /* Adjust handle color as desired */
    border-radius: 2px; /* Adjust handle border radius as desired */
}
        """)

        self.scroll_layout = QVBoxLayout(self.scroll_content)

        self.populate_color_maps()

        self.setLayout(self.layout)

        self.cmap = None

    def get_pixmap(self, color_map):
        gradient = np.linspace(0, 255, 256).astype(np.uint8)
        color_map_image = cv2.applyColorMap(gradient, color_map)

        # Rotate the color map image by -90 degrees
        rotated_image = cv2.rotate(color_map_image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        qimage = QImage(rotated_image.data, rotated_image.shape[1], rotated_image.shape[0],
                        rotated_image.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap(qimage)
        return pixmap

    def populate_color_maps(self):
        color_maps = [m for m in dir(cv2) if m.startswith('COLORMAP_')]

        cmap_none_frame = QFrame()
        cmap_none_layout = QHBoxLayout()
        cmap_none_frame.setLayout(cmap_none_layout)

        cmap_none_label = QLabel()
        font = QFont()
        font.setPointSize(8)
        cmap_none_label.setFont(font)
        cmap_none_label.setStyleSheet("color: rgb(255, 0, 0);")
        cmap_none_label.setCursor(Qt.ClosedHandCursor)
        cmap_none_label.setText("X - Do not apply color map")
        cmap_none_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        cmap_none_layout.addWidget(cmap_none_label)

        # event handlings for both labels
        cmap_none_label.mousePressEvent = lambda e, cmap=None: self.close_dialog(cmap)  # Set mouse click event
        cmap_none_label.enterEvent = lambda e, frame=cmap_none_frame, label=cmap_none_label: self.on_hover_enter(
            frame, label)  # Set mouse hover enter event
        cmap_none_label.leaveEvent = lambda e, frame=cmap_none_frame, label=cmap_none_label: self.on_hover_leave(
            frame, label)  # Set mouse hover leave event

        self.scroll_layout.addWidget(cmap_none_frame)

        for cmap in color_maps:
            cmap_frame = QFrame()
            cmap_layout = QHBoxLayout()
            cmap_frame.setLayout(cmap_layout)

            # Creating a QLabel for the color map name with rich text style
            cmap_label = QLabel()
            color_map_label = QLabel()

            cmap_label.setFixedSize(160, 35)
            cmap_label.setCursor(Qt.ClosedHandCursor)
            color_map_label.setCursor(Qt.ClosedHandCursor)

            font = QFont()
            font.setPointSize(8)
            cmap_label.setFont(font)

            cmap_label.setStyleSheet("color: %s;" % self.get_color_for_cmap(cmap))
            cmap_label.setText('<span style="background-color: transparent; padding: 2px;">%s</span>' % cmap.replace("COLORMAP_", ""))
            cmap_label.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
            cmap_layout.addWidget(cmap_label)

            color_map = getattr(cv2, cmap)

            pixmap = self.get_pixmap(color_map)

            color_map_label.setPixmap(pixmap)
            color_map_label.setFixedSize(250, 25)
            color_map_label.setScaledContents(True)  # Scale pixmap to fit QLabel
            cmap_layout.addWidget(color_map_label)

            # event handlings for both labels
            color_map_label.mousePressEvent = lambda e, cmap=color_map: self.close_dialog(cmap)  # Set mouse click event
            color_map_label.enterEvent = lambda e, frame=cmap_frame, label=cmap_label: self.on_hover_enter(
                frame, label)  # Set mouse hover enter event
            color_map_label.leaveEvent = lambda e, frame=cmap_frame, label=cmap_label: self.on_hover_leave(
                frame, label)  # Set mouse hover leave event

            cmap_label.mousePressEvent = lambda e, cmap=color_map: self.close_dialog(cmap)  # Set mouse click event
            cmap_label.enterEvent = lambda e, frame=cmap_frame, label=cmap_label: self.on_hover_enter(
                frame, label)  # Set mouse hover enter event
            cmap_label.leaveEvent = lambda e, frame=cmap_frame, label=cmap_label: self.on_hover_leave(
                frame, label)  # Set mouse hover leave event

            self.scroll_layout.addWidget(cmap_frame)

    def close_dialog(self, cmap):
        self.accept()
        self.cmap = cmap

    def get_cmap(self):
        return self.cmap

    def on_hover_enter(self, frame, label):
        font = label.font()
        font.setPointSize(10)
        label.setFont(font)
        frame.setStyleSheet("background:black; border-radius:5px")

    def on_hover_leave(self, frame, label):
        font = label.font()
        font.setPointSize(8)
        label.setFont(font)
        frame.setStyleSheet("background:white;opacity:1;")

    def get_color_for_cmap(self, cmap):
        # Function to get the color corresponding to a given color map name
        color_map = getattr(cv2, cmap)
        gradient = np.linspace(0, 255, 256).astype(np.uint8)
        color_map_image = cv2.applyColorMap(gradient, color_map)

        # Sample multiple points from the color map image
        num_samples = 100
        sample_points = [
            (np.random.randint(0, color_map_image.shape[0]), np.random.randint(0, color_map_image.shape[1])) for _ in
            range(num_samples)]

        # Calculate average color from sampled points
        avg_color = np.mean([color_map_image[y, x] for y, x in sample_points], axis=0)

        # Convert BGR color to RGB and normalize to range [0, 1]
        r, g, b = avg_color[::-1]  # Convert BGR to RGB
        r /= 255.0
        g /= 255.0
        b /= 255.0
        # Convert RGB to hex format
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
