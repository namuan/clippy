import sys
import os
import time
import random
import json

from PyQt6 import QtWidgets, QtCore, QtGui
from PIL import Image

from ..utils.image import GifHelper
from ..models.state import State
from ..api.client import GreetingClient
from ..utils.paths import DATA_FILE
from ..ui.components import SpeechBubble, PetWidget

# Load JSON Data
with open(DATA_FILE, "r", encoding="utf-8") as f:
    PETS_DATA = json.load(f)

# Pet controller
class Pet:
    def __init__(self, species, color, fps, size):
        self.hbitmaps = None
        self.frame_interval = None
        self.current_frame = None
        self.frame_count = None
        self.height = None
        self.width = None
        self.frames = None
        self.species = species
        self.color = color
        self.fps = fps
        self.size = size
        
        # Screen dimensions
        screen = QtWidgets.QApplication.primaryScreen()
        size = screen.size()
        self.screen_width = size.width()
        self.screen_height = size.height()

        species_data = PETS_DATA[species]
        defaults = species_data.get("defaults", {})
        self.STATES_INFO = {}
        for state_name, gif_path in species_data["states"][color].items():
            state_defaults = defaults.get(state_name, {})
            self.STATES_INFO[state_name] = {
                "gif": gif_path,
                "hold": state_defaults.get("hold", self.fps),
                "movement_speed": state_defaults.get("movement_speed", 0),
                "speed_animation": state_defaults.get("speed_animation", 1.0),
            }

        self.state = self.random_state(
            exception=["with_ball", "wallclimb", "walldig", "wallgrab", "wallnap", "fall_from_grab"])
        self.frame_animation()

        # Taskbar settings (simplified for non-Windows)
        self.taskbar_height = 60
        self.y_def = self.screen_height - self.height - self.taskbar_height
        self.y = self.screen_height - self.height - self.taskbar_height
        self.x = self.screen_width - self.width
        
        self.hwnd = None
        self.widget = PetWidget()
        self.widget.move(int(self.x), int(self.y))
        self.widget.show()

        self.immunity = False
        self.lie_duration = 24

        self.wall_scene_step = None
        self.scene_wallclimb = False
        self.fall_last_frame = None
        self.fall_last_hbitmap = None

        self.height_lie = 20
        
        self.bubble = SpeechBubble("", parent=None)
        self.bubble_visible = False
        self.api_client = GreetingClient()

    def random_state(self, exception=None):
        keys = list(self.STATES_INFO.keys())

        if exception:
            if isinstance(exception, str):
                exception = [exception]
            for ex in exception:
                if ex in keys:
                    keys.remove(ex)

        name = random.choice(keys)
        info = self.STATES_INFO[name]

        return State(
            name,
            info["gif"],
            hold=info["hold"],
            movement_speed=info["movement_speed"],
            speed_animation=info["speed_animation"],
            direction=random.choice([-1, 1]),
        )

    def draw_frame(self, hbitmap):
        if self.widget:
            self.widget.move(int(self.x), int(self.y))
            self.widget.update_image(hbitmap)

    def update_state(self):
        # Use PyQt to get global mouse position
        pos = QtGui.QCursor.pos()
        mouse_x, mouse_y = pos.x(), pos.y()

        distance = ((self.x - mouse_x) ** 2 + (self.y - mouse_y) ** 2) ** 0.5

        if self.wall_scene_step is not None:
            if self.wall_scene_step == "go_to_wall":
                if self.x < self.screen_width - self.width:
                    self.x += self.state.movement_speed
                    return
                info = self.STATES_INFO["wallclimb"]
                self.state = State("wallclimb", info["gif"], hold=info["hold"],
                                   movement_speed=info["movement_speed"],
                                   speed_animation=info["speed_animation"],
                                   direction=1)
                self.frame_animation()
                self.wall_scene_step = "wallclimb"
                return

            if self.wall_scene_step == "wallclimb":
                mid = self.screen_height // 2
                quarter = mid + self.screen_height // 4
                if quarter > self.y > mid:
                    if random.random() < 0.05:
                        mid = self.y
                    else:
                        self.y -= self.state.movement_speed
                        return
                elif self.y > mid:
                    self.y -= self.state.movement_speed
                    return

                info = self.STATES_INFO["walldig"]
                self.state = State("walldig", info["gif"], hold=info["hold"],
                                   movement_speed=info["movement_speed"], speed_animation=info["speed_animation"],
                                   direction=1)
                self.frame_animation()
                self.wall_scene_step = "walldig"
                return

            if self.wall_scene_step == "walldig" and self.state.next(self):
                info = self.STATES_INFO["wallnap"]
                self.state = State("wallnap", info["gif"], hold=info["hold"],
                                   movement_speed=info["movement_speed"], speed_animation=info["speed_animation"],
                                   direction=-1)
                self.frame_animation()
                self.wall_scene_step = "wallnap"
                return

            if self.wall_scene_step == "wallnap" and self.state.next(self):
                info = self.STATES_INFO["wallgrab"]
                self.state = State("wallgrab", info["gif"], hold=info["hold"],
                                   movement_speed=0, speed_animation=info["speed_animation"],
                                   direction=1)
                self.frame_animation()
                self.wall_scene_step = "wallgrab"
                return

            if self.wall_scene_step == "wallgrab" and self.state.next(self):
                info = self.STATES_INFO["fall_from_grab"]
                self.state = State("fall_from_grab", info["gif"], hold=info["hold"],
                                   movement_speed=info["movement_speed"],
                                   speed_animation=info["speed_animation"],
                                   direction=-1)
                self.frame_animation()
                self.fall_last_frame = self.frames[-1]
                self.fall_last_hbitmap = self.hbitmaps[-1]

                self.wall_scene_step = "fall_frame"
                return

            if self.wall_scene_step == "fall_frame":
                if self.y < self.y_def:
                    self.y += self.state.movement_speed
                    self.x -= self.state.movement_speed // 2

                    self.draw_frame(self.fall_last_hbitmap)
                    return

                self.y = self.y_def
                self.wall_scene_step = None
                self.immunity = False
                self.state = self.random_state(
                    exception=["with_ball", "wallclimb", "walldig",
                               "wallgrab", "wallnap", "fall_from_grab"]
                )
                self.frame_animation()
                return

        color_states = PETS_DATA[self.species]["states"][self.color]
        if "lie" in color_states and distance < self.height_lie and not self.immunity:
            gif_path = color_states["lie"]
            hold = self.lie_duration
            movement_speed = PETS_DATA[self.species]["defaults"].get("lie", {}).get("movement_speed", 0)
            speed_animation = PETS_DATA[self.species]["defaults"].get("lie", {}).get("speed_animation", 1.0)
            self.state = State("lie", gif_path, hold=hold, movement_speed=movement_speed,
                               speed_animation=speed_animation)
            self.immunity = True
            self.frame_animation()

        elif self.state.next(self):
            if self.bubble_visible:
                self.bubble.hide()
                self.bubble_visible = False

            if self.species == "clippy" and random.random() < 0.2:
                # Try to get dynamic greeting
                text = self.api_client.get_greeting()
                
                if text:
                    # Greeting logic
                    info = self.STATES_INFO.get("idle", list(self.STATES_INFO.values())[0])
                    if "idle" in self.STATES_INFO:
                         info = self.STATES_INFO["idle"]
                    
                    # Calculate hold frames for approx 4 seconds
                    target_duration = 4.0
                    speed = info.get("speed_animation", 1.0)
                    # Avoid division by zero if speed is 0
                    if speed == 0: speed = 1.0
                    
                    hold_frames = int(target_duration * self.fps * speed)
                    
                    self.state = State("idle", info["gif"], hold=hold_frames, movement_speed=0, speed_animation=speed)
                    self.frame_animation()
                    
                    # Show bubble
                    self.bubble.setText(text)
                    self.bubble.adjustSize()
                    # Position bubble near pet
                    bx = self.x - self.bubble.width()
                    by = self.y - self.bubble.height()
                    if bx < 0: bx = self.x + self.width
                    if by < 0: by = 0
                    self.bubble.move(int(bx), int(by))
                    self.bubble.show()
                    self.bubble_visible = True
                    return

            if random.random() < 0.005:
                self.wall_scene_step = "go_to_wall"
                return

            self.state = self.random_state()
            self.frame_animation()

    def frame_animation(self):
        self.frames = GifHelper.load_gif_frames(self.state.gif)
        
        # Resize if needed
        if self.size != "Original" and self.frames:
            # Scale factor
            # "Very Small", "Small", "Original", "Medium", "Big", "Really Big"
            scale = 1.0
            if self.size == "Very Small": scale = 0.5
            elif self.size == "Small": scale = 0.75
            elif self.size == "Medium": scale = 1.25
            elif self.size == "Big": scale = 1.5
            elif self.size == "Really Big": scale = 2.0
            
            if scale != 1.0:
                new_frames = []
                for f in self.frames:
                    w, h = f.size
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    new_frames.append(f.resize((new_w, new_h), Image.Resampling.LANCZOS))
                self.frames = new_frames

        self.hbitmaps = []
        for frame in self.frames:
            if self.state.direction < 0:
                frame = frame.transpose(Image.FLIP_LEFT_RIGHT)
            self.hbitmaps.append(GifHelper.pil_to_hbitmap(frame))

        self.current_frame = 0
        self.frame_count = len(self.frames)
        if self.frame_count > 0:
            self.width, self.height = self.frames[0].size
            self.frame_interval = 1.0 / (self.fps * self.state.speed_animation)
        else:
            self.width, self.height = 100, 100 # Fallback
            self.frame_interval = 0.1

    def close(self):
        if self.widget:
            self.widget.close()
        if self.bubble:
            self.bubble.close()
