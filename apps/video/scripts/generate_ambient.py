"""Generate an original 180-second, mono ambient bed using only Python stdlib."""

from array import array
from math import pi, sin
from pathlib import Path
import wave

RATE = 22_050
DURATION = 180
OUTPUT = Path(__file__).resolve().parents[1] / "public" / "ambient-original.wav"
CHORDS = ((55.0, 82.41, 110.0), (49.0, 73.42, 98.0), (65.41, 98.0, 130.81), (55.0, 82.41, 110.0))
NOTES = (220.0, 293.66, 349.23, 261.63, 392.0, 329.63, 246.94, 369.99)


def generate() -> None:
    samples = array("h")
    for frame in range(RATE * DURATION):
        t = frame / RATE
        segment = min(int(t // 45), len(CHORDS) - 1)
        chord = CHORDS[segment]
        if segment < len(CHORDS) - 1 and t % 45 > 40:
            blend = (t % 45 - 40) / 5
            blend = blend * blend * (3 - 2 * blend)
            chord = tuple(a * (1 - blend) + b * blend for a, b in zip(chord, CHORDS[segment + 1]))
        # Slow amplitude movement, a soft layered fifth, and sparse piano-like strikes.
        drone = sum(
            sin(2 * pi * hz * t + 0.12 * sin(2 * pi * 0.013 * t)) * (0.025 / (i + 1))
            for i, hz in enumerate(chord)
        )
        drone += 0.012 * sin(2 * pi * (chord[0] * 2) * t + 0.3 * sin(2 * pi * 0.009 * t))
        hit_index = int(t // 13)
        hit_time = hit_index * 13.0
        age = t - hit_time
        hit = 0.0
        if age < 3.2:
            f = NOTES[(hit_index * 3 + 1) % len(NOTES)]
            envelope = (1 - age / 3.2) ** 2 * min(age / 0.025, 1)
            hit = envelope * (0.11 * sin(2 * pi * f * age) + 0.035 * sin(2 * pi * f * 2.01 * age))
        fade = min(t / 4.0, (DURATION - t) / 5.0, 1.0)
        value = max(-0.8, min(0.8, (drone + hit) * 4 * max(0.0, fade)))
        samples.append(int(value * 32767))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUTPUT), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(RATE)
        audio.writeframes(samples.tobytes())


if __name__ == "__main__":
    generate()
