"""
brain.py — the personality layer. This is the part you'll customize the most
as you shape your robot's character. It wires sensor events to expressions,
movements, and speech.

Swap `respond_to_speech()` for a call to an LLM API if you want Coglet-style
conversational chat instead of canned replies — that's the one function to
change; everything else (face/servo/motor reactions) stays as-is.
"""

import random
import threading
import time

from face_display import Face
from motor_control import MotorController, make_pca9685
from servo_control import ServoRig
from imu_sensor import MotionMonitor
from voice_input import Listener, speak


CANNED_REPLIES = {
    "hello": "Hello! It's good to see you.",
    "how are you": "I'm doing great, thanks for asking!",
    "your name": "You can call me whatever you like, I'm still deciding on a name.",
}


class Robot:
    def __init__(self):
        pca = make_pca9685()
        self.face = Face()
        self.motors = MotorController(pca)
        self.servos = ServoRig(pca)
        self.listener = Listener()
        self._busy = threading.Lock()

        self.motion = MotionMonitor(
            on_shake=self.react_to_shake,
            on_tilt=self.react_to_tilt,
            on_level=self.react_to_level,
        )

    def start(self):
        self.motion.start()
        self.face.set_expression("neutral")
        self._voice_thread = threading.Thread(target=self._voice_loop, daemon=True)
        self._voice_thread.start()

    def shutdown(self):
        self.motion.stop()
        self.motors.stop()
        self.servos.center_all()
        self.face.stop()

    # -- reactive behaviors, triggered by the IMU -----------------------
    def react_to_shake(self):
        if self._busy.locked():
            return
        with self._busy:
            self.face.set_expression("surprised")
            self.servos.wiggle_ears()
            time.sleep(0.3)
            self.face.set_expression("neutral")

    def react_to_tilt(self):
        with self._busy:
            self.face.set_expression("surprised")
            self.motors.stop()  # don't keep driving while being handled

    def react_to_level(self):
        with self._busy:
            self.face.set_expression("happy")
            self.servos.nod()
            time.sleep(0.3)
            self.face.set_expression("neutral")

    # -- voice interaction loop ------------------------------------------
    def _voice_loop(self):
        while True:
            text = self.listener.listen_once()
            if not text:
                continue
            self.face.set_expression("listening")
            self.respond_to_speech(text.lower())
            self.face.set_expression("neutral")

    def respond_to_speech(self, text: str):
        reply = None
        for key, canned in CANNED_REPLIES.items():
            if key in text:
                reply = canned
                break
        if reply is None:
            reply = "I heard you, but I'm not sure how to respond to that yet."

        self._talk(reply)

    def _talk(self, text: str):
        with self._busy:
            self.face.set_expression("happy")
            # crude mouth animation while speaking: pulse level up/down
            def animate():
                for _ in range(int(len(text) / 8) + 3):
                    self.face.set_mouth_level(random.uniform(0.3, 1.0))
                    time.sleep(0.12)
                self.face.set_mouth_level(0)

            t = threading.Thread(target=animate, daemon=True)
            t.start()
            speak(text)
            t.join()

    # -- simple demo idle wander, optional --------------------------------
    def idle_wander(self, duration_s: float = 3.0):
        self.motors.forward(0.4)
        time.sleep(duration_s)
        self.motors.stop()
