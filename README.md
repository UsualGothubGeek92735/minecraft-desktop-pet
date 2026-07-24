# Minecraft Desktop Pet

A tiny always-on-top pixel-art pet that lives on your desktop.

- **18 mobs** across the Overworld, the Nether, the End, and more: Pig, Chicken,
  Creeper, Zombie Villager, Skeleton, Spider, Enderman, Witch, Piglin, Ghast,
  Shulker, Axolotl, Polar Bear, Blaze, Sniffer, Slime, Magma Cube, and the
  Sulfur Cube — switch with `<` `>`
- Each mob starts as a **baby** and grows into an **adult** the more you feed it
- **Feed** button raises hunger + growth; **click or drag your mouse over the sprite**
  to pet it (raises happiness)
- Drag the dark top bar to move it around your screen
- Stats are saved automatically, so your pets remember how you've treated them between launches
- Each mob appears **in its home biome or dimension** — the Piglin/Ghast/Blaze/Magma Cube
  stand in the Nether, the Enderman and Shulker sit in the End, the Sniffer is on a beach,
  the Sulfur Cube is in the Sulfur Caves, the Polar Bear is in snowy tundra, the Axolotl is
  in a lush cave, the Witch and Slime are in a swamp, and so on.
- **Two separate moods to watch for:**
  - **Grumpy** (hunger too low) — the window shakes and it nags you with popups until fed.
  - **Sad** (happiness too low, i.e. you haven't been petting it) — droopy eyes, a little
    tear, no misbehavior, just a quieter "I miss you" look. Pet it to cheer it back up.
  It will never close your other programs or touch your desktop icons — just be an
  annoying (or mopey) little gremlin until you take care of it.
- **The Creeper is special**: if you neglect it, instead of just shaking it flashes
  red/white and **explodes** in a little particle burst (still hungry afterward — it'll
  do it again until fed).
- **The Chicken is special too**: if you neglect it, it **throws an egg** across the
  window at you (an animated projectile that arcs and splats).
- **Whenever you close the app**, whichever mob is currently on screen flashes red/white
  and pops in a little particle burst as a goodbye. All of the above is purely cosmetic —
  nothing outside the pet's own window is ever touched.
- **Music & sound**: each biome has its own looping chiptune background track, plus sound
  effects for feeding, petting, growing up, egg throws, and explosions. Everything is
  procedurally generated from scratch in Python (no copyrighted Minecraft audio). Click the
  speaker icon in the top-right of the title bar to mute/unmute — your preference is
  remembered between launches.

## Files
- `pet_app.py` — the app itself, run this
- `sprites.py` — draws all the pixel-art sprites and biome backgrounds (generated in code)
- `audio_gen.py` — generates the music/SFX `.wav` files under `assets/` (already pre-built;
  you only need to rerun this if you want to tweak the sound)
- `assets/music/*.wav`, `assets/sfx/*.wav` — the pre-built audio files
- `icon.ico` — app icon (a happy creeper)
- `requirements.txt` — Python packages needed

## 1. Run it first (optional, to try it before building)

You need **Python 3.10-3.12** installed on Windows (get it from python.org - tick
"Add Python to PATH" during install; 3.11 is a safe, well-supported choice). Tkinter
comes bundled with Python on Windows, you don't need to install it separately.

Open a terminal (Command Prompt, PowerShell, or the VS Code terminal) in the folder
with these files:

```
pip install -r requirements.txt
python pet_app.py
```

A little pig should appear on your screen with background music playing. Click `>` to
cycle through mobs (the music changes with the biome), hit Feed, and try dragging your
mouse over the sprite to pet it.

If pygame (the audio library) fails to install or load for any reason, the app still
runs fine - it just runs silently instead of erroring out.

## 2. Turn it into a .exe with PyInstaller

Still in that same folder, run:

```
pyinstaller --onefile --windowed --icon=icon.ico --add-data "assets;assets" --name "MinecraftPet" pet_app.py
```

What the flags do:
- `--onefile` -> bundles everything into a single `.exe`
- `--windowed` -> no console window pops up behind your pet
- `--icon=icon.ico` -> gives the exe the creeper icon
- `--add-data "assets;assets"` -> **bundles the music/SFX files into the exe** (this is
  required - without it the built exe will run silently with no sound). Note the `;`
  semicolon - that's the Windows syntax. (On Mac/Linux this would be a `:` colon instead.)
- `--name "MinecraftPet"` -> names the output file `MinecraftPet.exe`

This takes 20-60 seconds. When it's done, your `.exe` is at:

```
dist\MinecraftPet.exe
```

Double-click that file and your pet launches - no Python needed on any machine
you copy it to. You can pin it to your Start Menu or set it to run at startup by
dropping a shortcut to it into:

```
shell:startup
```
(paste that into the Windows Run dialog, Win+R, and drop the shortcut in the folder that opens)

## Tuning the game feel

Open `pet_app.py` and look at the `CONFIG` section near the top - you can adjust:
- `FEED_HUNGER_GAIN` / `FEED_GROWTH_GAIN` - how much one Feed click helps
- `DECAY_INTERVAL_MS` / `HUNGER_DECAY` / `HAPPY_DECAY` - how fast pets get hungry/lonely over time
- `GRUMPY_HUNGER_THRESHOLD` - how low hunger has to drop before a mob gets grumpy
- `SAD_HAPPY_THRESHOLD` - how low happiness has to drop before a mob looks sad
- `GROWTH_TO_ADULT` - how much total feeding it takes for a baby to grow up

## Tweaking the music/sound

Everything under `assets/` is generated by `audio_gen.py` using plain math (square/
triangle/sine waves). To change a biome's melody, tempo, or instrument sound, edit the
`BIOME_MUSIC` dictionary near the top of `audio_gen.py`, then rerun:

```
python audio_gen.py
```

This overwrites the `.wav` files in `assets/` with freshly generated versions.
