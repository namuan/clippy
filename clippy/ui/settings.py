import json
import os
from PyQt6 import QtWidgets, QtCore
from ..utils.paths import DATA_FILE, LIST_FILE
from .components import PetCard

class PetSettingsTab(QtWidgets.QScrollArea):
    def __init__(self, main_window):
        super().__init__()
        self.setWidgetResizable(True)
        self.main_window = main_window

        self.container = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.container)

        self.grid_wrap = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(self.grid_wrap)
        self.grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.grid.setSpacing(14)
        self.layout.addWidget(self.grid_wrap)

        self.setWidget(self.container)
        
        self.load_data()

    def load_data(self):
        # Load Definitions
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Load Current State
        current_map = {}
        if os.path.exists(LIST_FILE):
            try:
                with open(LIST_FILE, "r", encoding="utf-8") as f:
                    current_data = json.load(f)
                    current_map = {p["species"]: p for p in current_data.get("pets", [])}
            except:
                pass

        self.blocks = []

        # Create Cards
        for species, info in data.items():
            if "colors" not in info:
                continue

            entry = current_map.get(species, {})
            enabled = entry.get("enabled", False)
            selected_colors = entry.get("colors", [])
            selected_size = entry.get("size", "Original")

            block = PetCard(species, info, enabled, selected_colors, selected_size)
            block.changed.connect(self.save)
            self.blocks.append(block)

        self.populate_grid()

    def populate_grid(self):
        # Clear existing
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                self.grid.removeWidget(w)
                w.setParent(None)

        # Calculate columns based on width
        width = self.viewport().width()
        col_count = max(1, width // 260)

        row = col = 0
        for block in self.blocks:
            self.grid.addWidget(block, row, col)
            col += 1
            if col >= col_count:
                col = 0
                row += 1

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.populate_grid()

    def save(self):
        result = {"pets": []}
        for block in self.blocks:
            result["pets"].append(block.get_data())

        with open(LIST_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)

        if self.main_window:
            self.main_window.start_refresh()


class SystemSettingsTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QtCore.QSettings("Clippy", "PetManager")
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        # Label
        label = QtWidgets.QLabel("Define Clippy's personality (System Prompt):")
        layout.addWidget(label)

        # Text Area
        self.prompt_input = QtWidgets.QPlainTextEdit()
        default_prompt = "You are Clippy. You are helpful, annoying, and observant. Generate a short, one-sentence greeting or observation for a programmer."
        saved_prompt = self.settings.value("system_prompt", default_prompt)
        self.prompt_input.setPlainText(saved_prompt)
        layout.addWidget(self.prompt_input)

        # Save Button
        self.save_btn = QtWidgets.QPushButton("Save Prompt")
        self.save_btn.clicked.connect(self.save_prompt)
        layout.addWidget(self.save_btn)
        
        layout.addStretch()
        self.setLayout(layout)

    def save_prompt(self):
        prompt = self.prompt_input.toPlainText()
        self.settings.setValue("system_prompt", prompt)
        
        # Feedback
        original_text = self.save_btn.text()
        self.save_btn.setText("Saved!")
        self.save_btn.setEnabled(False)
        
        QtCore.QTimer.singleShot(1500, lambda: self.reset_btn(original_text))

    def reset_btn(self, text):
        self.save_btn.setText(text)
        self.save_btn.setEnabled(True)


class Settings(QtWidgets.QTabWidget):
    def __init__(self, main_window):
        super().__init__()
        self.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)
        
        self.pet_tab = PetSettingsTab(main_window)
        self.system_tab = SystemSettingsTab()
        
        self.addTab(self.pet_tab, "Manage Pets")
        self.addTab(self.system_tab, "AI Personality")
