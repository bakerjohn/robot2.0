"""
servo_control.py — expressive servos (head pan/tilt, ears, etc.) on the same
PCA9685 that drives the motors. Angle limits from config.py protect your
mechanism from over-travel.
"""

import time
from adafruit_motor import servo

import config


class ServoRig:
    def __init__(self, pca):
        self._servos = {}
        for name, channel in config.SERVO_CHANNELS.items():
            lo, hi = config.SERVO_LIMITS.get(name, (0, 180))
            s = servo.Servo(pca.channels[channel], min_pulse=500, max_pulse=2500)
            self._servos[name] = s
            self._limits = getattr(self, "_limits", {})
            self._limits[name] = (lo, hi)
        self.center_all()

    def set_angle(self, name: str, angle: float):
        lo, hi = self._limits[name]
        angle = max(lo, min(hi, angle))
        self._servos[name].angle = angle

    def get_neutral(self, name: str) -> float:
        return config.SERVO_NEUTRAL.get(name, 90)

    def center(self, name: str):
        self.set_angle(name, self.get_neutral(name))

    def center_all(self):
        for name in self._servos:
            self.center(name)

    def sweep(self, name: str, start: float, end: float, duration_s: float = 0.5, steps: int = 20):
        """Smoothly move a servo from start to end over duration_s."""
        for i in range(steps + 1):
            t = i / steps
            angle = start + (end - start) * t
            self.set_angle(name, angle)
            time.sleep(duration_s / steps)

    def nod(self, name: str = "head_tilt", amount: float = 15, duration_s: float = 0.6):
        base = self.get_neutral(name)
        self.sweep(name, base, base - amount, duration_s / 2)
        self.sweep(name, base - amount, base, duration_s / 2)

    def shake_head(self, name: str = "head_pan", amount: float = 20, duration_s: float = 0.8):
        base = self.get_neutral(name)
        self.sweep(name, base, base + amount, duration_s / 4)
        self.sweep(name, base + amount, base - amount, duration_s / 2)
        self.sweep(name, base - amount, base, duration_s / 4)

    def wiggle_ears(self, duration_s: float = 0.5):
        for name in ("ear_left", "ear_right"):
            if name in self._servos:
                base = self.get_neutral(name)
                self.sweep(name, base, base + 20, duration_s / 2)
                self.sweep(name, base + 20, base, duration_s / 2)
