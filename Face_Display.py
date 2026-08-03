"""
face_display.py — draws a simple animated "face" (eyes + optional mouth bar)
on the I2C OLED, in the spirit of Coglet's expressive character but using a
screen instead of animatronic eyes.

If your "1107" OLED isn't SSD1306-compatible, swap the driver import below
for the matching luma driver (e.g. luma.oled.device.sh1106) — everything
else (the drawing code) stays the same.
"""

import time
import threading
import random

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw

import config


class Face:
    def __init__(self):
        serial = i2c(port=config.I2C_BUS, address=config.OLED_ADDR)
        self.device = ssd1306(serial, width=config.OLED_WIDTH, height=config.OLED_HEIGHT)
        self.w = config.OLED_WIDTH
        self.h = config.OLED_HEIGHT
        self._lock = threading.Lock()
        self._expression = "neutral"
        self._mouth_level = 0.0  # 0-1, driven by voice/talking amplitude
        self._stop_blink = threading.Event()
        self._blink_thread = threading.Thread(target=self._blink_loop, daemon=True)
        self._blink_thread.start()

    # -- public API ---------------------------------------------------
    def set_expression(self, name: str):
        with self._lock:
            self._expression = name
        self._render()

    def set_mouth_level(self, level: float):
        with self._lock:
            self._mouth_level = max(0.0, min(1.0, level))
        self._render()

    def stop(self):
        self._stop_blink.set()

    # -- internals ------------------------------------------------------
    def _blink_loop(self):
        while not self._stop_blink.is_set():
            wait = random.uniform(*config.BLINK_INTERVAL_RANGE_S)
            if self._stop_blink.wait(wait):
                break
            if self._expression in ("neutral", "happy"):
                self._blink_once()

    def _blink_once(self):
        prev = self._expression
        self._draw_eyes(open_amount=0.05)
        time.sleep(0.12)
        with self._lock:
            self._expression = prev
        self._render()

    def _render(self):
        img = Image.new("1", (self.w, self.h), 0)
        draw = ImageDraw.Draw(img)
        expr = self._expression

        eye_open = {
            "neutral": 1.0, "happy": 0.6, "sleepy": 0.3,
            "surprised": 1.3, "listening": 1.0, "sad": 0.7,
        }.get(expr, 1.0)

        self._draw_eyes(open_amount=eye_open, draw=draw)

        if self._mouth_level > 0.02:
            self._draw_mouth(draw, self._mouth_level)

        self.device.display(img)

    def _draw_eyes(self, open_amount, draw=None):
        standalone = draw is None
        if standalone:
            img = Image.new("1", (self.w, self.h), 0)
            draw = ImageDraw.Draw(img)

        cy = self.h * 0.42
        eye_w, eye_h = 26, 26 * open_amount
        spacing = self.w * 0.28

        for cx in (self.w / 2 - spacing, self.w / 2 + spacing):
            box = [cx - eye_w / 2, cy - eye_h / 2, cx + eye_w / 2, cy + eye_h / 2]
            draw.ellipse(box, fill=1)

        if standalone:
            self.device.display(img)

    def _draw_mouth(self, draw, level):
        mw = 40
        mh = 4 + int(level * 18)
        cx, cy = self.w / 2, self.h * 0.78
        draw.ellipse([cx - mw / 2, cy - mh / 2, cx + mw / 2, cy + mh / 2], fill=1)


if __name__ == "__main__":
    face = Face()
    for expr in ("neutral", "happy", "surprised", "sleepy", "sad"):
        print(expr)
        face.set_expression(expr)
        time.sleep(1.5)
