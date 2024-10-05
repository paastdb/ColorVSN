import os
import time

from PyQt5 import QtGui
from PyQt5.QtGui import QImage, QPixmap, QTransform
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QMessageBox

from app_classes.color_vsn_worker import ColorVSNWorker
from app_classes.ui_main_window import MainWindowUI
from views.main_window import Ui_MainWindow
from widgets.color_map_dialog import ColorMapDialog
from widgets.py_toggle import PyToggle


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui_main_window = MainWindowUI(self)

        self.extensions = ["MP4"]
        self.max_file_size = 3 * 1024 * 1024 * 1024  # 3 GB in bytes
        self.filename = None
        self.color_vsn_worker = None

        self.infrared_toggle = PyToggle(active_color="#16E900", bg_color="#A2A2A2")
        self.colormap_dialog = ColorMapDialog()

        self.setupUi(self)

    def setupUi(self, MainWindow):
        Ui_MainWindow.setupUi(self, MainWindow)

        self.horizontalLayout_infrared_toggle.addWidget(self.infrared_toggle)

        # INITIAL STATES
        self.label_colormap.setText("Select a color map")
        self.label_colormap.setStyleSheet("background-color:rgba(0,0,0,0.8);color:white")

        self.horizontalSlider_contrast.setValue(2)
        self.horizontalSlider_brightness.setValue(0)
        self.infrared_toggle.setChecked(True)

        # adding ui definitions
        self.ui_main_window.ui_definitions()

        # MINIMIZE
        self.minimizeAppBtn.clicked.connect(lambda: self.showMinimized())

        # MAXIMIZE/RESTORE
        self.maximizeRestoreAppBtn.clicked.connect(lambda: self.ui_main_window.maximize_restore())

        # CLOSE APPLICATION
        self.closeAppBtn.clicked.connect(lambda: self.close())

        # CLICK EVENT HANDLERS
        self.btn_start_processing.clicked.connect(self.start_color_vsn_worker_thread)
        self.btn_upload.clicked.connect(self.upload_file)

        # EVENT HANDLERS
        self.label_colormap.mousePressEvent = lambda e: self.select_colormap()
        self.lineEdit_output_folder.mousePressEvent = lambda e: self.select_output_folder()

        # Connect signals
        self.horizontalSlider_brightness.valueChanged.connect(self.update_brightness_icon)

    def update_brightness_icon(self, value):
        # Update icon rotation and size based on slider value
        rotation = value * 3.6  # Convert slider value to degrees (360 degrees for 100)
        # scale = 0.5 + (value / 200)  # Scale factor ranges from 0.5 to 1.0 based on slider value
        pixmap = QPixmap(':/icons/icons/brightness-icon.png')
        pixmap = pixmap.transformed(QTransform().rotate(rotation))
        # pixmap = pixmap.scaled(pixmap.width() * scale, pixmap.height() * scale, Qt.KeepAspectRatio)
        self.label_brightness_icon.setPixmap(pixmap)

    def select_colormap(self):
        self.colormap_dialog.exec_()
        cmap = self.colormap_dialog.get_cmap()
        if cmap is not None:
            self.label_colormap.setText("")
            pixmap = self.colormap_dialog.get_pixmap(self.colormap_dialog.get_cmap())
            self.label_colormap.setPixmap(pixmap)
            self.label_colormap.setStyleSheet("")
        else:
            self.label_colormap.setPixmap(QPixmap(None))
            self.label_colormap.setText("Select a color map")
            self.label_colormap.setStyleSheet("background-color:rgba(0,0,0,0.8);color:white")

    def select_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder_path:
            self.lineEdit_output_folder.setText(folder_path)

    def upload_file(self):
        path, _ = QFileDialog.getOpenFileName(self, self.tr("Choose Input Video File"), "",
                                              ";; ".join(list(map(lambda x: f"*.{str.lower(x)}", self.extensions))))
        if path:
            file_size = os.path.getsize(path)
            if file_size <= self.max_file_size:
                self.set_file(path)
            else:
                QMessageBox.warning(self, "File Size Exceeded", "Maximum file size exceeded (3 GB).")


    def start_color_vsn_worker_thread(self):
        self.color_vsn_worker = ColorVSNWorker(**{"filename": self.filename,
                                                                    "output_dir": self.lineEdit_output_folder.text(),
                                                                    "infrared": self.infrared_toggle.checkState(),
                                               "contrast": self.horizontalSlider_contrast.value(),
                                               "brightness": self.horizontalSlider_brightness.value(),
                                               "colormap": self.colormap_dialog.get_cmap()})
        self.color_vsn_worker.worker_signals.finished.connect(self.finished_slot)
        self.color_vsn_worker.worker_signals.status.connect(self.status_slot)
        self.color_vsn_worker.worker_signals.update.connect(self.update_slot)
        self.color_vsn_worker.is_running = True
        self.color_vsn_worker.start()
        return True

    def quit_color_vsn_worker_thread(self):
        if self.color_vsn_worker is not None and self.color_vsn_worker.isRunning():
            self.color_vsn_worker.terminate()
            time.sleep(1)
            self.color_vsn_worker.worker_signals.finished.disconnect(self.finished_slot)
            self.color_vsn_worker.worker_signals.update.disconnect(self.update_slot)
            self.color_vsn_worker.worker_signals.status.disconnect(self.status_slot)
            del self.color_vsn_worker
            self.color_vsn_worker = None

    def finished_slot(self, status, message):
        self.quit_color_vsn_worker_thread()


    def status_slot(self, status, message):
        pass

    def get_pixmap_from_frame(self, processed_frame):
        # Convert OpenCV image (BGR format) to QImage
        qImg = QImage(processed_frame.data, processed_frame.shape[1], processed_frame.shape[0], QImage.Format_BGR888)

        # Convert QImage to QPixmap
        pixmap = QPixmap.fromImage(qImg)
        return pixmap

    def update_slot(self, processed_frame):
        pixmap = self.get_pixmap_from_frame(processed_frame)
        # Set the pixmap to the label
        self.label_processed_frame.setPixmap(pixmap)

        # Resize the label to fit the pixmap
        self.label_processed_frame.setScaledContents(True)
        # self.progressBar.setValue(int(value))
        QApplication.processEvents()

    def set_file(self, filename):
        self.filename = filename
        self.label_filename.show()
        self.label_filename.setText(self.filename)

    def get_filename(self):
        return self.filenameworker_signals.py

    def process_video(self):
        pass

    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent) -> None:
        filepath = a0.mimeData().urls()[0].toString().replace("file:///", "")
        extension = filepath.split(".")[-1]
        if extension in self.extensions:
            self.set_file(filepath)
    
    def resizeEvent(self, event):
        # Update Size Grips
        self.ui_main_window.left_grip.setGeometry(0, 5, 5, self.height())
        self.ui_main_window.right_grip.setGeometry(self.width() - 5, 5, 5, self.height())
        self.ui_main_window.top_grip.setGeometry(0, 0, self.width(), 5)
        self.ui_main_window.bottom_grip.setGeometry(0, self.height() - 5, self.width(), 5)

    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()



