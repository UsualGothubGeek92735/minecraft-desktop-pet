"""
Minecraft-themed Desktop Pet
-----------------------------
A tiny always-on-top desktop companion. Feed it, pet it (click or drag your
mouse over it), and watch it grow from a baby into an adult. Ignore its
hunger too long and it gets grumpy and annoying (shaking window + nagging
popups) until you feed it again. Ignore *petting* it and it gets sad and
droopy instead (a gentler, separate mood from hunger-grumpy). The Creeper is
special: when neglected, or whenever you close the app, it flashes red/white
and pops in a little particle burst -- purely cosmetic, it never touches
anything outside its own window. Each mob has its own looping chiptune
background music matching its home biome/dimension, plus sound effects for
feeding, petting, growing, and more (all procedurally generated, no
copyrighted audio). Click the speaker icon in the title bar to mute.

Run with:  python pet_app.py
Package with PyInstaller (see README.md) to get a standalone .exe.
"""

import json
import math
import os
import random
import sys
import tkinter as tk
from tkinter import font as tkfont

try:
    import ctypes
except ImportError:
    ctypes = None

try:
    import pygame
    _PYGAME_OK = True
except ImportError:
    pygame = None
    _PYGAME_OK = False

from PIL import ImageTk

import sprites

# ----------------------------------------------------------------- CONFIG
MOBS = ["pig", "chicken", "creeper", "zombie_villager",
        "skeleton", "spider", "enderman", "witch",
        "piglin", "ghast", "shulker", "axolotl", "polar_bear",
        "blaze", "sniffer", "slime", "magma_cube", "sulfur_cube"]
GROWTH_TO_ADULT = 100          # growth points needed to become an adult
FEED_HUNGER_GAIN = 18
FEED_GROWTH_GAIN = 9
FEED_HAPPY_GAIN = 4
PET_HAPPY_GAIN = 6

DECAY_INTERVAL_MS = 4000        # how often stats tick down
HUNGER_DECAY = 1.4
HAPPY_DECAY = 0.8

GRUMPY_HUNGER_THRESHOLD = 22
SAD_HAPPY_THRESHOLD = 35        # below this (and not grumpy-hungry) the mob looks sad/lonely
HAPPY_MOOD_THRESHOLD = 70

ANIM_INTERVAL_MS = 160          # idle bob speed
SHAKE_CHECK_MS = 6000           # how often a grumpy mob might shake
NAG_COOLDOWN_MS = 25000         # min gap between nag popups
PET_DRAG_COOLDOWN_MS = 350      # min gap between happiness ticks while dragging over the pet

EXPLODE_FLASH_MS = 130          # speed of the red/white pre-explosion flicker
EXPLODE_FLASH_COUNT = 6         # how many flickers before it pops
PARTICLE_COUNT = 14

WINDOW_W, WINDOW_H = 168, 236
SPRITE_SIZE = 150

NAG_LINES = {
    "pig": ["Oink!! I'm STARVING.", "Feed me or I'll roll in your taskbar.", "This pig is not happy."],
    "chicken": ["Catch this! *throws egg*", "BAWK! Incoming egg!", "Feed me before I redecorate with eggs."],
    "creeper": ["Ssss... I'm hungry, not happy.", "Feed me before I get grumpy for real.",
                "A hungry creeper is a cranky creeper."],
    "zombie_villager": ["Hnnngh... feed... me...", "So... hungry...", "Ugh. Ugh. FEED. ME."],
    "skeleton": ["*rattle rattle* FEED ME.", "These bones are hangry.", "I'm all bones AND grumpy now."],
    "spider": ["Hisssss... hungry...", "Eight legs, zero food.", "Feed me before I get skittish."],
    "enderman": ["...hungry...", "Don't look at me. Just feed me.", "*teleports impatiently*"],
    "witch": ["My cauldron is EMPTY, feed me!", "Hunger makes my potions worse.", "Feed me, or else... (I'll just sulk)"],
    "piglin": ["*grunts angrily*", "Where's my gold... and my FOOD?", "Feed me or I'm bartering elsewhere."],
    "ghast": ["*sad ghast noises*", "I cry when I'm hungry. A lot.", "Feed me before I get weepy."],
    "shulker": ["*rattles inside shell*", "Hungry AND levitating you in spirit.", "Feed me, or stay shelled out."],
    "axolotl": ["*sad little axolotl noises*", "My gills are drooping, feed me.", "Hungry axolotl, activate: pout."],
    "polar_bear": ["*grumpy bear growl*", "Feed me before I raid your fridge.", "Cold, tired, and hungry. Feed me."],
    "blaze": ["*angry flame crackling*", "My fire's dying out -- feed me!", "Hangry AND on fire. Feed me."],
    "sniffer": ["*grumpy sniffing noises*", "This nose smells... nothing. Feed me.", "Ancient AND hungry. Feed me."],
    "slime": ["*aggressive squelching*", "Feed me before I bounce on your desktop.", "Hangry slime, activate: wobble."],
    "magma_cube": ["*molten grumbling*", "Feed me before I really heat up.", "Hangry and lava-hot. Feed me."],
    "sulfur_cube": ["*confused grumpy squelch*", "Even confused, I know I'm hungry.", "Feed me. That part I'm sure of."],
}

EGG_LINES = ["SPLAT! An egg hit you!", "Direct hit! Feed the chicken!", "Egg-cellent throw, chicken.",
             "Yolk's on you -- feed me!"]

GROW_LINES = "{name} grew up! Say hello to the adult {mob}!"


def _left_mouse_down():
    """Check the real OS mouse-button state (Windows only). This lets us
    detect dragging over the pet even in areas made click-through by the
    window's transparent-color background, which normal Tk mouse events
    can't see."""
    if ctypes and sys.platform.startswith("win"):
        try:
            return bool(ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000)
        except Exception:
            return False
    return False


def resource_path(*parts):
    """Locate a bundled file whether running from source or from a
    PyInstaller-frozen .exe (which unpacks assets into sys._MEIPASS)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, *parts)


def settings_path():
    if sys.platform.startswith("win"):
        base = os.getenv("APPDATA") or os.path.expanduser("~")
    else:
        base = os.path.expanduser("~")
    d = os.path.join(base, "MinecraftDesktopPet")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "settings.json")


def load_settings():
    path = settings_path()
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_settings(settings):
    try:
        with open(settings_path(), "w") as f:
            json.dump(settings, f)
    except Exception:
        pass


def save_path():
    if sys.platform.startswith("win"):
        base = os.getenv("APPDATA") or os.path.expanduser("~")
    else:
        base = os.path.expanduser("~")
    d = os.path.join(base, "MinecraftDesktopPet")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "save.json")


DEFAULT_STATE = {
    mob: {"hunger": 80, "happiness": 80, "growth": 0, "stage": "baby"} for mob in MOBS
}


def load_state():
    path = save_path()
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
            for mob in MOBS:
                if mob not in data:
                    data[mob] = dict(DEFAULT_STATE[mob])
            return data
        except Exception:
            pass
    return {k: dict(v) for k, v in DEFAULT_STATE.items()}


def save_state(state):
    try:
        with open(save_path(), "w") as f:
            json.dump(state, f)
    except Exception:
        pass


class DesktopPet:
    def __init__(self, root):
        self.root = root
        self.state = load_state()
        self.mob_index = 0
        self.anim_tick = 0
        self.drag_offset = (0, 0)
        self.last_nag = 0
        self.last_pet_time = 0
        self.exploding = False
        self.sprite_cache = {}
        self.prev_mood = {}
        self.current_music_biome = None
        self.muted = load_settings().get("muted", False)
        self.sfx = {}
        self.audio_ok = False

        self._init_audio()
        self._setup_window()
        self._build_ui()
        self._refresh_sprite()
        self._update_bars()
        self._play_biome_music()

        self.root.after(ANIM_INTERVAL_MS, self._animate)
        self.root.after(DECAY_INTERVAL_MS, self._decay_tick)
        self.root.after(SHAKE_CHECK_MS, self._maybe_misbehave)
        self.root.after(120, self._pet_poll)

    # ------------------------------------------------------------ audio --
    def _init_audio(self):
        if not _PYGAME_OK:
            return
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=512)
            pygame.mixer.init()
            for name in ("feed", "pet", "grow", "egg_whoosh", "egg_splat",
                         "explode", "nag", "sad"):
                path = resource_path("assets", "sfx", f"{name}.wav")
                if os.path.exists(path):
                    self.sfx[name] = pygame.mixer.Sound(path)
            self.audio_ok = True
        except Exception:
            self.audio_ok = False

    def _play_sfx(self, name):
        if self.audio_ok and not self.muted and name in self.sfx:
            try:
                self.sfx[name].play()
            except Exception:
                pass

    def _play_biome_music(self):
        if not self.audio_ok:
            return
        biome = sprites.BIOME_OF_MOB.get(self.mob)
        if biome is None or biome == self.current_music_biome:
            return
        self.current_music_biome = biome
        path = resource_path("assets", "music", f"{biome}.wav")
        if not os.path.exists(path):
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.0 if self.muted else 0.8)
            pygame.mixer.music.play(loops=-1)
        except Exception:
            pass

    def _toggle_mute(self):
        self.muted = not self.muted
        if self.audio_ok:
            try:
                pygame.mixer.music.set_volume(0.0 if self.muted else 0.8)
            except Exception:
                pass
        if hasattr(self, "mute_lbl"):
            self.mute_lbl.config(text="\U0001F507" if self.muted else "\U0001F50A")
        save_settings({"muted": self.muted})

    # ---------------------------------------------------------- window --
    def _setup_window(self):
        r = self.root
        r.overrideredirect(True)
        r.attributes("-topmost", True)
        r.geometry(f"{WINDOW_W}x{WINDOW_H}+200+200")
        self.bg_key = "#ff00fe"  # magenta chroma-key
        r.config(bg=self.bg_key)
        try:
            r.attributes("-transparentcolor", self.bg_key)
        except tk.TclError:
            pass  # not supported on this platform; window will just show bg color

    def _build_ui(self):
        bg = self.bg_key
        f = self.root

        # drag handle / title strip
        top = tk.Frame(f, bg="#2b2b2b", height=18)
        top.pack(fill="x")
        top.pack_propagate(False)
        self.title_lbl = tk.Label(top, text="Pig", bg="#2b2b2b", fg="white",
                                   font=("Segoe UI", 9, "bold"))
        self.title_lbl.pack(side="left", padx=6)
        close_btn = tk.Label(top, text="x", bg="#2b2b2b", fg="#e06060",
                              font=("Segoe UI", 9, "bold"), cursor="hand2")
        close_btn.pack(side="right", padx=6)
        close_btn.bind("<Button-1>", lambda e: self._quit())

        self.mute_lbl = tk.Label(top, text="\U0001F507" if self.muted else "\U0001F50A",
                                  bg="#2b2b2b", fg="white", font=("Segoe UI", 9), cursor="hand2")
        self.mute_lbl.pack(side="right", padx=2)
        self.mute_lbl.bind("<Button-1>", lambda e: self._toggle_mute())

        for widget in (top, self.title_lbl):
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._do_drag)

        # sprite canvas
        self.canvas = tk.Canvas(f, width=SPRITE_SIZE, height=SPRITE_SIZE,
                                 bg=bg, highlightthickness=0)
        self.canvas.pack()
        self.sprite_img_id = self.canvas.create_image(SPRITE_SIZE // 2, SPRITE_SIZE // 2 + 6,
                                                        image=None)
        self.canvas.bind("<Button-1>", self._on_pet_click)
        self.canvas.bind("<B1-Motion>", self._on_pet_drag)

        # stat bars
        bars = tk.Frame(f, bg=bg)
        bars.pack(fill="x", padx=8, pady=(2, 0))
        self.hunger_bar = self._make_bar(bars, "Hunger", "#e0a339")
        self.happy_bar = self._make_bar(bars, "Happy", "#4caf50")

        # controls
        ctrl = tk.Frame(f, bg=bg)
        ctrl.pack(fill="x", pady=(4, 4))
        prev_btn = tk.Button(ctrl, text="<", width=2, command=self._prev_mob)
        prev_btn.pack(side="left", padx=(8, 0))
        feed_btn = tk.Button(ctrl, text="Feed", command=self._feed, bg="#6ab04c", fg="white")
        feed_btn.pack(side="left", expand=True, fill="x", padx=4)
        next_btn = tk.Button(ctrl, text=">", width=2, command=self._next_mob)
        next_btn.pack(side="right", padx=(0, 8))

    def _make_bar(self, parent, label, color):
        row = tk.Frame(parent, bg=self.bg_key)
        row.pack(fill="x", pady=1)
        tk.Label(row, text=label, bg=self.bg_key, fg="white",
                 font=("Segoe UI", 7), width=6, anchor="w").pack(side="left")
        canvas = tk.Canvas(row, width=90, height=8, bg="#3a3a3a", highlightthickness=0)
        canvas.pack(side="left")
        bar = canvas.create_rectangle(0, 0, 90, 8, fill=color, width=0)
        return {"canvas": canvas, "bar": bar, "color": color}

    # ------------------------------------------------------------ drag --
    def _start_drag(self, event):
        self.drag_offset = (event.x, event.y)

    def _do_drag(self, event):
        x = self.root.winfo_pointerx() - self.drag_offset[0]
        y = self.root.winfo_pointery() - self.drag_offset[1]
        self.root.geometry(f"+{x}+{y}")

    # -------------------------------------------------------- mob logic --
    @property
    def mob(self):
        return MOBS[self.mob_index]

    def _prev_mob(self):
        if self.exploding:
            return
        self.mob_index = (self.mob_index - 1) % len(MOBS)
        self._refresh_sprite()
        self._update_bars()
        self._play_biome_music()

    def _next_mob(self):
        if self.exploding:
            return
        self.mob_index = (self.mob_index + 1) % len(MOBS)
        self._refresh_sprite()
        self._update_bars()
        self._play_biome_music()

    def _mood(self, mob=None):
        mob = mob or self.mob
        s = self.state[mob]
        if s["hunger"] < GRUMPY_HUNGER_THRESHOLD:
            return "grumpy"
        if s["hunger"] > HAPPY_MOOD_THRESHOLD and s["happiness"] > HAPPY_MOOD_THRESHOLD:
            return "happy"
        if s["happiness"] < SAD_HAPPY_THRESHOLD:
            return "sad"
        return "neutral"

    def _get_sprite_img(self, mob, stage, mood):
        key = (mob, stage, mood)
        if key not in self.sprite_cache:
            pil_img = sprites.get_sprite(mob, stage, mood)
            pil_img = pil_img.resize((SPRITE_SIZE, SPRITE_SIZE))
            self.sprite_cache[key] = ImageTk.PhotoImage(pil_img)
        return self.sprite_cache[key]

    def _refresh_sprite(self):
        if self.exploding:
            return
        s = self.state[self.mob]
        mood = self._mood()
        if mood == "sad" and self.prev_mood.get(self.mob) != "sad":
            self._play_sfx("sad")
        self.prev_mood[self.mob] = mood
        img = self._get_sprite_img(self.mob, s["stage"], mood)
        self.canvas.itemconfig(self.sprite_img_id, image=img)
        self.title_lbl.config(
            text=f"{sprites.MOB_NAMES[self.mob]} ({s['stage']})"
        )

    def _update_bars(self):
        s = self.state[self.mob]
        for key, bar in (("hunger", self.hunger_bar), ("happiness", self.happy_bar)):
            pct = max(0, min(100, s[key])) / 100
            bar["canvas"].coords(bar["bar"], 0, 0, 90 * pct, 8)
            color = bar["color"] if pct > 0.25 else "#c0392b"
            bar["canvas"].itemconfig(bar["bar"], fill=color)

    # ------------------------------------------------------- animation --
    def _animate(self):
        self.anim_tick += 1
        offset = int(4 * math.sin(self.anim_tick / 4))
        self.canvas.coords(self.sprite_img_id, SPRITE_SIZE // 2, SPRITE_SIZE // 2 + 6 + offset)
        self.root.after(ANIM_INTERVAL_MS, self._animate)

    def _float_text(self, text, color="#ffffff"):
        lbl = tk.Label(self.root, text=text, fg=color, bg=self.bg_key,
                        font=("Segoe UI", 10, "bold"))
        x = WINDOW_W // 2 - 10
        y = 60
        lbl.place(x=x, y=y)

        def step(n=0):
            if n > 14:
                lbl.destroy()
                return
            lbl.place(x=x, y=y - n * 3)
            self.root.after(35, lambda: step(n + 1))

        step()

    # ------------------------------------------------------------- care --
    def _feed(self):
        if self.exploding:
            return
        s = self.state[self.mob]
        s["hunger"] = min(100, s["hunger"] + FEED_HUNGER_GAIN)
        s["happiness"] = min(100, s["happiness"] + FEED_HAPPY_GAIN)
        self._play_sfx("feed")
        if s["stage"] == "baby":
            s["growth"] = min(GROWTH_TO_ADULT, s["growth"] + FEED_GROWTH_GAIN)
            if s["growth"] >= GROWTH_TO_ADULT:
                s["stage"] = "adult"
                self._float_text("GREW UP!", "#ffd54f")
                self._play_sfx("grow")
                self._toast(GROW_LINES.format(name=sprites.MOB_NAMES[self.mob],
                                               mob=sprites.MOB_NAMES[self.mob].lower()))
        else:
            self._float_text("+food", "#8bd17c")
        self._refresh_sprite()
        self._update_bars()
        save_state(self.state)

    def _now_ms(self):
        return int(self.root.tk.call("clock", "milliseconds"))

    def _on_pet_click(self, event):
        self._apply_pet()

    def _on_pet_drag(self, event):
        # only pet while the cursor is actually still over the sprite canvas
        if not (0 <= event.x <= SPRITE_SIZE and 0 <= event.y <= SPRITE_SIZE):
            return
        now = self._now_ms()
        if now - self.last_pet_time < PET_DRAG_COOLDOWN_MS:
            return
        self.last_pet_time = now
        self._apply_pet()

    def _apply_pet(self):
        if self.exploding:
            return
        s = self.state[self.mob]
        s["happiness"] = min(100, s["happiness"] + PET_HAPPY_GAIN)
        self._play_sfx("pet")
        self._float_text(random.choice(["<3", "^_^", ":)"]), "#ff8fab")
        self._refresh_sprite()
        self._update_bars()
        save_state(self.state)

    def _pet_poll(self):
        """Backup path for drag-petting: polls the real OS mouse state so it
        still works over the window's transparent (click-through) padding,
        not just the solid parts of the sprite."""
        if not self.exploding and _left_mouse_down():
            mx, my = self.root.winfo_pointerx(), self.root.winfo_pointery()
            cx0, cy0 = self.canvas.winfo_rootx(), self.canvas.winfo_rooty()
            if cx0 <= mx <= cx0 + SPRITE_SIZE and cy0 <= my <= cy0 + SPRITE_SIZE:
                now = self._now_ms()
                if now - self.last_pet_time >= PET_DRAG_COOLDOWN_MS:
                    self.last_pet_time = now
                    self._apply_pet()
        self.root.after(120, self._pet_poll)

    # ---------------------------------------------------------- decay --
    def _decay_tick(self):
        for mob in MOBS:
            s = self.state[mob]
            s["hunger"] = max(0, s["hunger"] - HUNGER_DECAY)
            extra = HAPPY_DECAY * (1.6 if s["hunger"] < GRUMPY_HUNGER_THRESHOLD else 1.0)
            s["happiness"] = max(0, s["happiness"] - extra)
        self._refresh_sprite()
        self._update_bars()
        save_state(self.state)
        self.root.after(DECAY_INTERVAL_MS, self._decay_tick)

    # ------------------------------------------------------- misbehave --
    def _maybe_misbehave(self):
        if self._mood() == "grumpy" and not self.exploding:
            now = self._now_ms()
            if self.mob == "creeper":
                if now - self.last_nag > NAG_COOLDOWN_MS:
                    self.last_nag = now
                    self._creeper_meltdown()
            elif self.mob == "chicken":
                self._shake_window()
                if now - self.last_nag > NAG_COOLDOWN_MS:
                    self.last_nag = now
                    self._chicken_tantrum()
            else:
                self._shake_window()
                if now - self.last_nag > NAG_COOLDOWN_MS:
                    self.last_nag = now
                    self._play_sfx("nag")
                    self._toast(random.choice(NAG_LINES[self.mob]))
        self.root.after(SHAKE_CHECK_MS, self._maybe_misbehave)

    def _shake_window(self, n=0):
        if n > 8:
            return
        x = self.root.winfo_x() + random.randint(-4, 4)
        y = self.root.winfo_y() + random.randint(-2, 2)
        self.root.geometry(f"+{x}+{y}")
        self.root.after(40, lambda: self._shake_window(n + 1))

    def _toast(self, message):
        t = tk.Toplevel(self.root)
        t.overrideredirect(True)
        t.attributes("-topmost", True)
        rx, ry = self.root.winfo_x(), self.root.winfo_y()
        t.geometry(f"220x50+{rx + WINDOW_W + 8}+{ry + 20}")
        frame = tk.Frame(t, bg="#2b2b2b", highlightbackground="#6ab04c", highlightthickness=2)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text=f"{sprites.MOB_NAMES[self.mob]} says:", bg="#2b2b2b",
                 fg="#8bd17c", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=8, pady=(6, 0))
        tk.Label(frame, text=message, bg="#2b2b2b", fg="white", wraplength=200,
                 font=("Segoe UI", 9), justify="left").pack(anchor="w", padx=8)
        t.after(4200, t.destroy)

    # ------------------------------------------------------- chicken --
    def _chicken_tantrum(self):
        """Neglect behavior unique to the chicken: it lobs an egg across
        the window at you. Purely cosmetic -- the egg never leaves this
        canvas or touches anything else on your screen."""
        if self.mob != "chicken":
            return
        direction = random.choice([-1, 1])
        start_x = SPRITE_SIZE // 2 + direction * 20
        start_y = SPRITE_SIZE // 2 - 10
        egg = self.canvas.create_oval(start_x - 5, start_y - 6, start_x + 5, start_y + 6,
                                       fill="#fdf6e3", outline="#d8c9a0", width=1)
        vx = direction * random.uniform(4.5, 6.5)
        vy = random.uniform(-6.0, -3.5)
        gravity = 0.9

        def step(x=start_x, y=start_y, vx=vx, vy=vy):
            vy2 = vy + gravity
            x2, y2 = x + vx, y + vy2
            if x2 < -10 or x2 > SPRITE_SIZE + 10 or y2 > SPRITE_SIZE + 10:
                self.canvas.delete(egg)
                self._egg_splat(max(0, min(SPRITE_SIZE, x2)))
                return
            self.canvas.coords(egg, x2 - 5, y2 - 6, x2 + 5, y2 + 6)
            self.root.after(35, lambda: step(x2, y2, vx, vy2))

        step()
        self._play_sfx("egg_whoosh")
        self._toast(random.choice(EGG_LINES))

    def _egg_splat(self, x):
        self._play_sfx("egg_splat")
        splat = self.canvas.create_oval(x - 3, SPRITE_SIZE - 6, x + 3, SPRITE_SIZE,
                                         fill="#fdf6e3", outline="", width=0)

        def grow(n=0):
            if n > 6:
                self.canvas.delete(splat)
                return
            r = 3 + n * 2
            self.canvas.coords(splat, x - r, SPRITE_SIZE - 3 - r // 2, x + r, SPRITE_SIZE - 3 + r // 2)
            self.root.after(45, lambda: grow(n + 1))

        grow()

    # ---------------------------------------------------- creeper boom --
    def _flash_creeper(self, stage, n=0, on_done=None):
        """Alternate the on-screen sprite between normal and white/red 'charge'
        frames -- the classic Minecraft creeper pre-explosion flicker."""
        mood = "charge" if n % 2 == 0 else "neutral"
        img = self._get_sprite_img("creeper", stage, mood)
        self.canvas.itemconfig(self.sprite_img_id, image=img)
        if n >= EXPLODE_FLASH_COUNT:
            self._particle_burst(on_done)
            return
        self.root.after(EXPLODE_FLASH_MS, lambda: self._flash_creeper(stage, n + 1, on_done))

    def _particle_burst(self, on_done=None):
        self._play_sfx("explode")
        cx, cy = SPRITE_SIZE // 2, SPRITE_SIZE // 2 + 6
        self.canvas.itemconfig(self.sprite_img_id, image="")
        colors = ["#ff8a3d", "#ffd54f", "#ff5a3c", "#fff2b0"]
        particles = []
        for _ in range(PARTICLE_COUNT):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(2.5, 6.5)
            size = random.randint(4, 9)
            oval = self.canvas.create_oval(cx - size, cy - size, cx + size, cy + size,
                                            fill=random.choice(colors), width=0)
            particles.append({"id": oval, "x": cx, "y": cy,
                               "dx": math.cos(angle) * speed, "dy": math.sin(angle) * speed,
                               "size": size})

        def step(frame=0):
            if frame >= 12:
                for p in particles:
                    self.canvas.delete(p["id"])
                if on_done:
                    on_done()
                return
            for p in particles:
                p["x"] += p["dx"]
                p["y"] += p["dy"]
                shrink = max(1, p["size"] - frame)
                self.canvas.coords(p["id"], p["x"] - shrink, p["y"] - shrink,
                                    p["x"] + shrink, p["y"] + shrink)
            self.root.after(40, lambda: step(frame + 1))

        step()

    def _creeper_meltdown(self):
        """Neglect behavior unique to the creeper: it flashes and pops instead
        of just shaking the window. Purely visual -- nothing outside this
        window is touched, and it's still hungry (and can explode again)
        until you feed it."""
        if self.exploding or self.mob != "creeper":
            return
        self.exploding = True
        stage = self.state["creeper"]["stage"]
        self._shake_window()

        def after_boom():
            self.exploding = False
            self._refresh_sprite()
            self._toast("You made me explode! I'm still hungry though...")

        self._flash_creeper(stage, on_done=after_boom)

    def _farewell_explosion(self, done_callback):
        """Fun goodbye animation played whenever the window is closed:
        whichever mob is on screen flashes white/red and pops in a
        particle burst before the app exits."""
        self.exploding = True
        mob_name = sprites.MOB_NAMES[self.mob]
        self.title_lbl.config(text=f"{mob_name} (bye!)")

        flash_rect = self.canvas.create_rectangle(
            0, 0, SPRITE_SIZE, SPRITE_SIZE, fill="#ffffff", outline="", state="hidden"
        )

        def flash(n=0):
            if n >= EXPLODE_FLASH_COUNT:
                self.canvas.delete(flash_rect)
                self._particle_burst(done_callback)
                return
            color = "#ffffff" if n % 2 == 0 else "#ff4d3d"
            self.canvas.itemconfig(flash_rect, fill=color, state="normal")
            self.root.after(EXPLODE_FLASH_MS, lambda: _hide_then_next(n))

        def _hide_then_next(n):
            self.canvas.itemconfig(flash_rect, state="hidden")
            self.root.after(EXPLODE_FLASH_MS, lambda: flash(n + 1))

        flash()

    # -------------------------------------------------------------- quit --
    def _quit(self):
        if self.exploding:
            return
        save_state(self.state)
        self._farewell_explosion(self.root.destroy)


def main():
    root = tk.Tk()
    root.title("Minecraft Desktop Pet")
    try:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception:
        pass
    app = DesktopPet(root)
    root.protocol("WM_DELETE_WINDOW", app._quit)
    root.mainloop()


if __name__ == "__main__":
    main()
