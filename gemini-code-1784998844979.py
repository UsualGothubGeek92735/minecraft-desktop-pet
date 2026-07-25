import os
import sys
import tkinter as tk
import random
import pygame

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MinecraftPet:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Desktop Pet")
        
        # Configure transparent, borderless window
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        
        # Cross-platform transparency support
        if sys.platform.startswith('win'):
            self.root.wm_attributes("-transparentcolor", "white")
            self.bg_color = "white"
        else:
            self.root.wm_attributes("-transparent", True)
            self.bg_color = "systemTransparent"
            
        self.root.config(bg=self.bg_color)

        # Initialize Pygame Mixer for sound effects
        pygame.mixer.init()
        
        # --- LOAD SOUNDS (using resource_path) ---
        self.sounds = {}
        sound_files = {
            "ambient": resource_path("sounds/ambient.wav"),
            "hurt": resource_path("sounds/hurt.wav")
        }
        
        for name, path in sound_files.items():
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"Could not load sound {path}: {e}")

        # --- LOAD SPRITES (using resource_path) ---
        self.sprites = {}
        sprite_files = {
            "idle": resource_path("assets/idle.png"),
            "walk_left": resource_path("assets/walk_left.png"),
            "walk_right": resource_path("assets/walk_right.png")
        }

        for state, path in sprite_files.items():
            if os.path.exists(path):
                try:
                    self.sprites[state] = tk.PhotoImage(file=path)
                except Exception as e:
                    print(f"Could not load image {path}: {e}")

        # Fallback label if no image exists
        self.label = tk.Label(self.root, bg=self.bg_color, bd=0)
        self.label.pack()

        if "idle" in self.sprites:
            self.label.config(image=self.sprites["idle"])
        else:
            self.label.config(text="[Pet]", font=("Arial", 16), fg="green")

        # Window position state
        self.x = 200
        self.y = 200
        self.root.geometry(f"+{self.x}+{self.y}")

        # Movement and interaction bindings
        self.label.bind("<Button-1>", self.on_click)
        self.label.bind("<B1-Motion>", self.on_drag)

        # Play ambient sound on startup if available
        self.play_sound("ambient")

        # Start main loop
        self.animate()

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def on_click(self, event):
        self.play_sound("hurt")

    def on_drag(self, event):
        # Allow dragging the pet around the screen
        deltax = event.x - self.x
        deltay = event.y - self.y
        self.x = self.root.winfo_pointerx() - 25
        self.y = self.root.winfo_pointery() - 25
        self.root.geometry(f"+{self.x}+{self.y}")

    def animate(self):
        # Simple random movement behavior
        move = random.choice(["idle", "left", "right", "idle"])
        
        if move == "left":
            self.x -= 10
            if "walk_left" in self.sprites:
                self.label.config(image=self.sprites["walk_left"])
        elif move == "right":
            self.x += 10
            if "walk_right" in self.sprites:
                self.label.config(image=self.sprites["walk_right"])
        else:
            if "idle" in self.sprites:
                self.label.config(image=self.sprites["idle"])

        self.root.geometry(f"+{self.x}+{self.y}")
        
        # Random ambient sound trigger (5% chance per tick)
        if random.random() < 0.05:
            self.play_sound("ambient")

        # Repeat animation loop every 500ms
        self.root.after(500, self.animate)

if __name__ == "__main__":
    root = tk.Tk()
    pet = MinecraftPet(root)
    root.mainloop()