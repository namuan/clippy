from PIL import Image
import os

def convert_png_to_ico(source, target):
    try:
        img = Image.open(source)
        img.save(target, format='ICO', sizes=[(256, 256)])
        print(f"Successfully converted {source} to {target}")
    except Exception as e:
        print(f"Error converting image: {e}")

if __name__ == "__main__":
    # Adjust paths as needed
    source_file = "assets/clippy-icon.png"
    target_file = "assets/icon.ico"
    
    if os.path.exists(source_file):
        convert_png_to_ico(source_file, target_file)
    else:
        print(f"Source file not found: {source_file}")
