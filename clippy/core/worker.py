import json
import time
from PyQt6 import QtCore
from PIL import Image

from ..controllers.pet import Pet
from ..utils.image import GifHelper
from ..utils.paths import LIST_FILE

FPS_DEFAULT = 8
SIZE_DEFAULT = "small"

class PetWorker(QtCore.QObject):
    def __init__(self, pets):
        super().__init__()
        self.pets = pets
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_pets)
        self.running = True

    def start(self):
        self.running = True
        self.timer.start(10)  # Check every 10ms

    def update_pets(self):
        if not self.running:
            self.timer.stop()
            return
            
        now = time.time()
        for pet in self.pets:
            if now - getattr(pet, "last_update", 0) >= pet.frame_interval:
                pet.last_update = now
                pet.update_state()
                frame_idx = pet.current_frame
                if pet.state.direction < 0:
                    flipped = pet.frames[frame_idx].transpose(Image.FLIP_LEFT_RIGHT)
                    hbitmap = GifHelper.pil_to_hbitmap(flipped)
                    pet.draw_frame(hbitmap)
                else:
                    pet.draw_frame(pet.hbitmaps[frame_idx])
                pet.current_frame = (pet.current_frame + 1) % pet.frame_count

    def stop(self):
        self.running = False
        self.timer.stop()

    def wait(self):
        pass  # Compatibility with QThread


def load_pets():
    try:
        with open(LIST_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except FileNotFoundError:
        return []

    pets = []
    for entry in cfg.get("pets", []):
        if not entry.get("enabled", True):
            continue
        species = entry["species"]
        fps = entry.get("fps", FPS_DEFAULT)
        size = entry.get("size", SIZE_DEFAULT)
        for color in entry.get("colors", []):
            pets.append(Pet(species, color, fps, size))
    return pets
