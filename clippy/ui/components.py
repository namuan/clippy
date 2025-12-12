from PyQt6 import QtWidgets, QtCore, QtGui
from ..utils.assets import load_icon

class SpeechBubble(QtWidgets.QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.WindowType.ToolTip |
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_ShowWithoutActivating)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QtWidgets.QLabel(text)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(300)  # Constrain width to force wrapping
        self.label.setStyleSheet("""
            background-color: #FFFFE1;
            border: 1px solid black;
            border-radius: 5px;
            padding: 5px;
            font-family: Arial;
            font-size: 12px;
            color: black;
        """)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def setText(self, text):
        self.label.setText(text)
        self.label.adjustSize()
        self.adjustSize()


class PetWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_ShowWithoutActivating)
        # Make the window transparent for mouse events to match Windows behavior (click-through)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        self.label = QtWidgets.QLabel(self)
        self.label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.setLayout(layout)
        
    def update_image(self, pil_image):
        if not pil_image:
            return
        data = pil_image.convert("RGBA").tobytes("raw", "RGBA")
        qimage = QtGui.QImage(data, pil_image.width, pil_image.height, QtGui.QImage.Format.Format_RGBA8888)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        self.label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())


class ColorGrid(QtWidgets.QWidget):
    changed = QtCore.pyqtSignal()

    def __init__(self, colors, selected):
        super().__init__()
        layout = QtWidgets.QGridLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)

        self.buttons = {}
        cols = 4
        r = c = 0

        for col in colors:
            b = QtWidgets.QPushButton(col)
            b.setCheckable(True)
            b.setChecked(col in selected)
            b.setMinimumWidth(50)
            b.clicked.connect(self.changed.emit)
            layout.addWidget(b, r, c)
            self.buttons[col] = b

            c += 1
            if c >= cols:
                c = 0
                r += 1

    def get_selected(self):
        return [c for c, b in self.buttons.items() if b.isChecked()]


class PetCard(QtWidgets.QFrame):
    changed = QtCore.pyqtSignal()

    SIZES = ["Very Small", "Small", "Original", "Medium", "Big", "Really Big"]

    def __init__(self, species, info, enabled, selected_colors, selected_size):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.species = species
        self.available_colors = info.get("colors", [])

        # Main Layout
        layout = QtWidgets.QVBoxLayout(self)

        # 1. Icon
        icon_path = load_icon(species)
        icon_lbl = QtWidgets.QLabel()
        if icon_path:
            pix = QtGui.QPixmap(icon_path)
            if not pix.isNull():
                pix = pix.scaled(
                    72, 72,
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation
                )
                icon_lbl.setPixmap(pix)
            else:
                icon_lbl.setText("[no icon]")
        else:
            icon_lbl.setText("[no icon]")
        layout.addWidget(icon_lbl, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        # 2. Checkbox (Enable/Disable)
        title = species.capitalize()
        self.checkbox = QtWidgets.QCheckBox(title)
        self.checkbox.setChecked(enabled)
        self.checkbox.stateChanged.connect(self.changed.emit)
        layout.addWidget(self.checkbox, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        # 3. Size Selector
        self.size_selector = QtWidgets.QComboBox()
        self.size_selector.addItems(self.SIZES)
        if selected_size in self.SIZES:
            self.size_selector.setCurrentText(selected_size)
        else:
            self.size_selector.setCurrentText("Original")
        self.size_selector.currentIndexChanged.connect(self.changed.emit)
        layout.addWidget(self.size_selector)

        # 4. Color Grid (if applicable)
        if len(self.available_colors) > 1:
            self.color_widget = ColorGrid(self.available_colors, selected_colors)
            self.color_widget.changed.connect(self.changed.emit)
            layout.addWidget(self.color_widget)
        else:
            self.color_widget = None

        self.setMinimumWidth(180)
        self.setMaximumWidth(280)

    def get_data(self):
        # Determine colors
        if self.color_widget:
            colors = self.color_widget.get_selected()
        else:
            colors = self.available_colors[:]

        return {
            "species": self.species,
            "colors": colors,
            "enabled": self.checkbox.isChecked(),
            "size": self.size_selector.currentText()
        }
