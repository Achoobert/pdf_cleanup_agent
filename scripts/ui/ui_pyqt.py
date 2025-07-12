import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon
import os


def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle('PDF Power Converter')
    # Try to set an icon if available
    icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'app_icon.png')
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    layout = QVBoxLayout()
    label = QLabel('Hello, World!')
    layout.addWidget(label)
    window.setLayout(layout)
    window.resize(300, 100)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main() 