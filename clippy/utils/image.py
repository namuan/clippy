import os
from PIL import Image
from .paths import BASE_DIR

class GifHelper:
    @staticmethod
    def load_gif_frames(path):
        # path is expected to be relative to BASE_DIR (e.g., "media/clippy/...")
        abs_path = os.path.join(BASE_DIR, path)
        img = Image.open(abs_path)
        frames = []
        try:
            while True:
                frame = img.convert("RGBA")
                frames.append(frame)
                img.seek(img.tell() + 1)
        except EOFError:
            pass
        return frames

    @staticmethod
    def pil_to_hbitmap(frame: Image.Image):
        return frame  # Return the PIL image directly on non-Windows platforms
