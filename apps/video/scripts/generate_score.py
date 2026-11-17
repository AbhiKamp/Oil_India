"""Generate the original 60-second score for the short cut, using only the Python stdlib.

Space-organ mood: clock ticks, a pipe-organ wavetable, an eighth-note arpeggio that builds,
a hard cut to silence, then a resolving major chord. All material is original and deterministic.
Timing grid: 96 BPM, one bar = 2.5 s, so video cuts can land on bar lines.
"""

from array import array
from math import pi, sin
from pathlib import Path
import random
import wave

RATE = 32_000
DURATION = 60.0
BAR = 2.5
EIGHTH = BAR / 8
OUTPUT = Path(__file__).resolve().parents[1] / "public" / "score-original.wav"

# Organ wavetable: flue-pipe partials, one cycle.
TABLE_SIZE = 4096
PARTIALS = ((1, 1.0), (2, 0.55), (3, 0.28), (4, 0.22), (6, 0.1), (8, 0.07))
TABLE = [sum(w * sin(2 * pi * h * i / TABLE_SIZE) for h, w in PARTIALS) for i in range(TABLE_SIZE)]


def hz(midi: int) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


# Am, F, C, Em (MIDI chord tones, root position low voicing).
CHORDS = ((57, 60, 64), (53, 57, 60), (48, 52, 55), (52, 55, 59))
FINAL = (57, 61, 64)  # A major resolution
ARP = (0, 2, 0, 1, 2, 0, 1, 2)


def intensity(t: float) -> float:
    """Overall build: quiet open, rising arpeggio, climax at 45-50 s."""
    if t < 10:
        return 0.35 + 0.02 * t
    if t < 45:
        return 0.55 + 0.45 * (t - 10) / 35
    return 1.0


def add_tone(buf: list[float], start: float, length: float, freq: float, amp: float,
             attack: float, release: float) -> None:
    i0 = int(start * RATE)
    n = int((length + release) * RATE)
    step = freq * TABLE_SIZE / RATE
    phase = 0.0
    for k in range(n):
        i = i0 + k
        if i >= len(buf):
            break
        t = k / RATE
        env = min(t / attack, 1.0) if attack else 1.0
        if t > length:
            env *= max(0.0, 1 - (t - length) / release)
        buf[i] += amp * env * TABLE[int(phase) % TABLE_SIZE]
        phase += step


def add_tick(buf: list[float], start: float, amp: float, pitch: float, rng: random.Random) -> None:
    i0 = int(start * RATE)
    for k in range(int(0.03 * RATE)):
        if i0 + k >= len(buf):
            break
        t = k / RATE
        env = (1 - t / 0.03) ** 6
        buf[i0 + k] += amp * env * (0.6 * sin(2 * pi * pitch * t) + 0.4 * (rng.random() * 2 - 1))


def reverb(dry: list[float], delays: tuple[int, ...]) -> list[float]:
    """Schroeder reverb: four parallel combs then two allpasses."""
    out = [0.0] * len(dry)
    for d in delays[:4]:
        line = [0.0] * d
        for i, x in enumerate(dry):
            y = line[i % d]
            line[i % d] = x + 0.82 * y
            out[i] += y * 0.25
    for d in delays[4:]:
        line = [0.0] * d
        for i, x in enumerate(out):
            y = line[i % d]
            v = x + 0.6 * y
            line[i % d] = v
            out[i] = y - 0.6 * v
    return out


def generate() -> None:
    rng = random.Random(26121)
    n = int(DURATION * RATE)
    music = [0.0] * n
    ticks = [0.0] * n

    # Clock ticks every beat until the 50 s cut, plus one lone tick in the silence.
    beat = BAR / 4
    for b in range(int(50 / beat)):
        t = b * beat
        add_tick(ticks, t, 0.22 * intensity(t), 2400 if b % 2 else 1900, rng)
    add_tick(ticks, 51.25, 0.3, 1900, rng)

    # Bars 0-19 (0-50 s): pedal, pad, and arpeggio over the progression.
    for bar in range(20):
        t0 = bar * BAR
        chord = CHORDS[bar % 4] if bar >= 4 else CHORDS[0]
        lvl = intensity(t0)
        add_tone(music, t0, BAR, hz(chord[0] - 24), 0.16 * lvl, 0.4, 0.4)  # pedal
        for note in chord:
            add_tone(music, t0, BAR, hz(note), 0.045 * lvl, 0.8 if bar < 4 else 0.15, 0.6)
        if bar >= 4:  # arpeggio enters at 10 s
            for e, idx in enumerate(ARP):
                octave = 12 if e in (4, 5, 6, 7) and bar >= 10 else 0
                add_tone(music, t0 + e * EIGHTH, EIGHTH * 0.9, hz(chord[idx] + 12 + octave),
                         0.07 * lvl, 0.01, 0.25)
        if bar >= 14:  # high octave doubling for the climax
            add_tone(music, t0, BAR, hz(chord[0] + 24), 0.05 * lvl, 0.3, 0.5)

    # Hard cut at 50 s.
    cut = int(50 * RATE)
    fade = int(0.04 * RATE)
    for i in range(cut - fade, n):
        music[i] *= max(0.0, (cut - i) / fade)

    # Final A major swell from 52.5 s, fading out by 60 s.
    for note in FINAL:
        add_tone(music, 52.5, 4.0, hz(note), 0.07, 1.2, 3.4)
    add_tone(music, 52.5, 4.0, hz(FINAL[0] - 24), 0.16, 1.5, 3.4)
    add_tone(music, 52.5, 4.0, hz(FINAL[0] + 12), 0.04, 2.0, 3.4)

    dry = [m + k for m, k in zip(music, ticks)]
    wet_l = reverb(dry, (1557, 1617, 1491, 1422, 225, 556))
    wet_r = reverb(dry, (1580, 1640, 1514, 1445, 248, 579))

    peak = max(max(abs(0.7 * d + 0.55 * w) for d, w in zip(dry, wet)) for wet in (wet_l, wet_r))
    gain = 0.85 / peak
    samples = array("h")
    for i in range(n):
        tail = min(1.0, (DURATION - i / RATE) / 0.5)  # no click at the very end
        for wet in (wet_l, wet_r):
            samples.append(int(32767 * gain * tail * (0.7 * dry[i] + 0.55 * wet[i])))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUTPUT), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(samples.tobytes())


if __name__ == "__main__":
    generate()
    print(f"wrote {OUTPUT}")
