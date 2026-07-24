"""
Procedural audio generator.

Everything here is synthesized from scratch with plain math (square / triangle
/ sine waves + noise bursts) -- no copyrighted Minecraft audio is used or
referenced. Run this once to (re)build the .wav assets under assets/music
and assets/sfx. The app ships with pre-built assets, so players never need
to run this themselves -- it's here so the sound can be tweaked or regenerated.

Usage:  python audio_gen.py
"""

import math
import os
import random
import struct
import wave

SAMPLE_RATE = 22050
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def _write_wav(path, samples):
    """samples: list of floats in [-1, 1]"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        frames = b"".join(struct.pack("<h", max(-32000, min(32000, int(s * 32000)))) for s in samples)
        w.writeframes(frames)


def _envelope(n, attack=0.05, release=0.2):
    """Return a per-sample volume multiplier so notes don't click."""
    a = max(1, int(n * attack))
    r = max(1, int(n * release))
    env = []
    for i in range(n):
        if i < a:
            env.append(i / a)
        elif i > n - r:
            env.append(max(0.0, (n - i) / r))
        else:
            env.append(1.0)
    return env


def _tone(freq, duration_s, wave_type="square", volume=0.35):
    n = int(SAMPLE_RATE * duration_s)
    env = _envelope(n)
    out = []
    for i in range(n):
        t = i / SAMPLE_RATE
        phase = (t * freq) % 1.0
        if wave_type == "square":
            v = 1.0 if phase < 0.5 else -1.0
        elif wave_type == "triangle":
            v = 4 * abs(phase - 0.5) - 1
        else:  # sine
            v = math.sin(2 * math.pi * phase)
        out.append(v * volume * env[i])
    return out


def _noise(duration_s, volume=0.4, low_pass=False):
    n = int(SAMPLE_RATE * duration_s)
    env = _envelope(n, attack=0.02, release=0.6)
    out = []
    prev = 0.0
    for i in range(n):
        s = random.uniform(-1, 1)
        if low_pass:
            s = prev * 0.6 + s * 0.4
            prev = s
        out.append(s * volume * env[i])
    return out


def _sweep(f_start, f_end, duration_s, wave_type="sine", volume=0.35):
    n = int(SAMPLE_RATE * duration_s)
    env = _envelope(n, attack=0.05, release=0.3)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / n
        freq = f_start + (f_end - f_start) * t
        phase += freq / SAMPLE_RATE
        p = phase % 1.0
        if wave_type == "square":
            v = 1.0 if p < 0.5 else -1.0
        else:
            v = math.sin(2 * math.pi * p)
        out.append(v * volume * env[i])
    return out


def _mix(*tracks):
    length = max(len(t) for t in tracks)
    out = [0.0] * length
    for t in tracks:
        for i, s in enumerate(t):
            out[i] += s
    return [max(-1.0, min(1.0, s)) for s in out]


def _concat(*tracks):
    out = []
    for t in tracks:
        out.extend(t)
    return out


NOTE = 261.63  # C4


def semis(n):
    return NOTE * (2 ** (n / 12))


# ----------------------------------------------------------- biome music --
SCALES = {
    "major_penta": [0, 2, 4, 7, 9, 12],
    "minor_penta": [0, 3, 5, 7, 10, 12],
    "major": [0, 2, 4, 5, 7, 9, 11, 12],
    "minor": [0, 2, 3, 5, 7, 8, 10, 12],
    "phrygian": [0, 1, 3, 5, 7, 8, 10, 12],
    "whole_tone": [0, 2, 4, 6, 8, 10, 12],
}

BIOME_MUSIC = {
    "plains":       dict(root=261.63, scale="major_penta", wave="triangle", note_s=0.34, notes=16, rest=0.12, vol=0.30),
    "beach":        dict(root=293.66, scale="major_penta", wave="sine",     note_s=0.38, notes=16, rest=0.15, vol=0.28),
    "snowy":        dict(root=293.66, scale="major",       wave="sine",     note_s=0.42, notes=14, rest=0.20, vol=0.26),
    "village_night":dict(root=220.00, scale="minor",       wave="triangle", note_s=0.36, notes=16, rest=0.15, vol=0.28),
    "swamp":        dict(root=207.65, scale="phrygian",    wave="square",   note_s=0.40, notes=14, rest=0.20, vol=0.22),
    "cave":         dict(root=196.00, scale="minor_penta", wave="square",   note_s=0.46, notes=12, rest=0.35, vol=0.18),
    "lush_cave":    dict(root=246.94, scale="minor_penta", wave="triangle", note_s=0.38, notes=14, rest=0.18, vol=0.26),
    "end":          dict(root=261.63, scale="whole_tone",  wave="sine",     note_s=0.55, notes=10, rest=0.30, vol=0.22),
    "nether_waste": dict(root=164.81, scale="phrygian",    wave="square",   note_s=0.28, notes=18, rest=0.05, vol=0.30),
    "nether_soul":  dict(root=174.61, scale="whole_tone",  wave="triangle", note_s=0.50, notes=12, rest=0.30, vol=0.22),
    "sulfur_cave":  dict(root=196.00, scale="minor",       wave="square",   note_s=0.40, notes=14, rest=0.20, vol=0.24),
}


def build_biome_track(name, params):
    rng = random.Random(f"biome-{name}")
    scale = SCALES[params["scale"]]
    track = []
    prev_degree_idx = 0
    for i in range(params["notes"]):
        if rng.random() < params["rest"]:
            n = int(SAMPLE_RATE * params["note_s"])
            track.append([0.0] * n)
            continue
        # gentle melodic walk instead of pure random jumps
        step = rng.choice([-2, -1, -1, 0, 1, 1, 2])
        idx = max(0, min(len(scale) - 1, prev_degree_idx + step))
        prev_degree_idx = idx
        degree = scale[idx]
        octave_shift = rng.choice([0, 0, 0, 12]) if rng.random() < 0.15 else 0
        freq = params["root"] * (2 ** ((degree + octave_shift) / 12))
        track.append(_tone(freq, params["note_s"], params["wave"], params["vol"]))
    return _concat(*track)


def gen_music():
    for name, params in BIOME_MUSIC.items():
        samples = build_biome_track(name, params)
        _write_wav(os.path.join(OUT_DIR, "music", f"{name}.wav"), samples)
        print(f"  music/{name}.wav  ({len(samples)/SAMPLE_RATE:.1f}s loop)")


# ------------------------------------------------------------------ sfx --
def gen_sfx():
    sfx = {}

    # feed: quick two-note "chomp"
    sfx["feed"] = _concat(_tone(semis(-4), 0.07, "square", 0.35),
                           _tone(semis(-8), 0.09, "square", 0.35))

    # pet: soft ascending chime
    sfx["pet"] = _concat(_tone(semis(4), 0.08, "sine", 0.25),
                          _tone(semis(9), 0.10, "sine", 0.25))

    # grow: little fanfare arpeggio
    sfx["grow"] = _concat(_tone(semis(0), 0.10, "triangle", 0.30),
                           _tone(semis(4), 0.10, "triangle", 0.30),
                           _tone(semis(7), 0.10, "triangle", 0.30),
                           _tone(semis(12), 0.18, "triangle", 0.32))

    # egg whoosh: quick downward sweep
    sfx["egg_whoosh"] = _sweep(1400, 500, 0.28, "sine", 0.25)

    # egg splat: short noise burst
    sfx["egg_splat"] = _mix(_noise(0.18, volume=0.35, low_pass=True),
                             _tone(180, 0.08, "square", 0.15))

    # explosion boom: low noise + falling square tone
    sfx["explode"] = _mix(_noise(0.45, volume=0.5, low_pass=True),
                           _sweep(220, 60, 0.4, "square", 0.3))

    # nag blip: short double beep
    sfx["nag"] = _concat(_tone(880, 0.06, "square", 0.20),
                          [0.0] * int(SAMPLE_RATE * 0.03),
                          _tone(880, 0.06, "square", 0.20))

    # sad whimper: descending minor-third dip
    sfx["sad"] = _concat(_tone(semis(0), 0.14, "sine", 0.22),
                          _tone(semis(-3), 0.22, "sine", 0.20))

    for name, samples in sfx.items():
        _write_wav(os.path.join(OUT_DIR, "sfx", f"{name}.wav"), samples)
        print(f"  sfx/{name}.wav  ({len(samples)/SAMPLE_RATE:.2f}s)")


if __name__ == "__main__":
    print("Generating biome music...")
    gen_music()
    print("Generating sound effects...")
    gen_sfx()
    print("Done.")
