
# GLOBALS
# ///////////////////////////////////////////////////////////////
from PyQt5.QtCore import Qt, QEvent, QTimer
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QSizeGrip

from widgets import CustomGrip

GLOBAL_STATE = False
GLOBAL_TITLE_BAR = True


class MainWindowUI:
    def __init__(self, ui):
        self.ui = ui

    def maximize_restore(self):
        global GLOBAL_STATE
        status = GLOBAL_STATE
        if not status:
            self.ui.showMaximized()
            GLOBAL_STATE = True
            self.ui.appMargins.setContentsMargins(0, 0, 0, 0)
            self.ui.maximizeRestoreAppBtn.setToolTip("Restore")
            self.ui.frame_size_grip.hide()
            self.left_grip.hide()
            self.right_grip.hide()
            self.top_grip.hide()
            self.bottom_grip.hide()
        else:
            GLOBAL_STATE = False
            self.ui.showNormal()
            self.ui.resize(self.ui.width()+1, self.ui.height()+1)
            self.ui.appMargins.setContentsMargins(5, 5, 5, 5)
            self.ui.maximizeRestoreAppBtn.setToolTip("Maximize")
            self.ui.frame_size_grip.show()
            self.left_grip.show()
            self.right_grip.show()
            self.top_grip.show()
            self.bottom_grip.show()

    # RETURN STATUS
    # ///////////////////////////////////////////////////////////////
    def returStatus(self):
        return GLOBAL_STATE

    # SET STATUS
    # ///////////////////////////////////////////////////////////////
    def setStatus(self, status):
        global GLOBAL_STATE
        GLOBAL_STATE = status

    def ui_definitions(self):
        def dobleClickMaximizeRestore(event):
            # IF DOUBLE CLICK CHANGE STATUS
            if event.type() == QEvent.MouseButtonDblClick:
                QTimer.singleShot(250, lambda: self.maximize_restore())
        self.ui.titleRightInfo.mouseDoubleClickEvent = dobleClickMaximizeRestore

        # STANDARD TITLE BAR
        self.ui.setWindowFlags(Qt.FramelessWindowHint)
        self.ui.setAttribute(Qt.WA_TranslucentBackground)

        # MOVE WINDOW / MAXIMIZE / RESTORE
        def moveWindow(event):
            # IF MAXIMIZED CHANGE TO NORMAL
            if self.returStatus():
                self.maximize_restore()
            # MOVE WINDOW
            if event.buttons() == Qt.LeftButton:
                self.ui.move(self.ui.pos() + event.globalPos() - self.ui.dragPos)
                self.ui.dragPos = event.globalPos()
                event.accept()
        self.ui.titleRightInfo.mouseMoveEvent = moveWindow

        # CUSTOM GRIPS
        self.left_grip = CustomGrip(self.ui, Qt.LeftEdge, True)
        self.right_grip = CustomGrip(self.ui, Qt.RightEdge, True)
        self.top_grip = CustomGrip(self.ui, Qt.TopEdge, True)
        self.bottom_grip = CustomGrip(self.ui, Qt.BottomEdge, True)

        # DROP SHADOW
        self.shadow = QGraphicsDropShadowEffect(self.ui)
        self.shadow.setBlurRadius(17)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        # self.ui.bgApp.setGraphicsEffect(self.shadow)

        # RESIZE WINDOW
        self.sizegrip = QSizeGrip(self.ui.frame_size_grip)
        self.sizegrip.setStyleSheet("width: 20px; height: 20px; margin 0px; padding: 0px;")