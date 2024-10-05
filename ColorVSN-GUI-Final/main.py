import os
import sys
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

def resolve_path(path):
    if getattr(sys, "frozen", False):
        # If the 'frozen' flag is set, we are in bundled-app mode!
        resolved_path = os.path.abspath(os.path.join(sys._MEIPASS, path))
    else:
        # Normal development mode. Use os.getcwd() or __file__ as appropriate in your case...
        resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))

    return resolved_path


doc_log_path = os.path.expanduser('~')

output = open(resolve_path(os.path.join(doc_log_path,"logs.txt")), "wt")
if os.name == 'nt':  # Check if the operating system is Windows
    # Set the hidden attribute for the file
    import ctypes
    FILE_ATTRIBUTE_HIDDEN = 0x02
    ret = ctypes.windll.kernel32.SetFileAttributesW(resolve_path("logs.txt"), FILE_ATTRIBUTE_HIDDEN)
    if not ret:
        print("Error: Unable to set file attribute to hidden")


# https://stackoverflow.com/questions/74997331/moviepy-dont-works-in-exe-file-made-by-autopytoexe-pyinstaller-with-hide-conso
sys.stdout = output
sys.stderr = output

from controllers.main_window import MainWindow


#  Specifically for windows to show icon taskbar as well
try:
    import ctypes
    myappid = 'color-svn.v.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


if __name__ == "__main__":
    import multiprocessing
    # Call freeze_support or Pyinstaller will recursively fork infinite processes forever
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont(":/fonts/fonts/Thunder-ExtraBoldLCItalic.ttf")
    app.setWindowIcon(QIcon(":/logos/logos/vsn.png"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
