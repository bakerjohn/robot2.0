"""
config.py — single place to match this code to YOUR exact wiring.

Everything downstream (motor_control, servo_control, face_display, imu_sensor)
imports from here. If something moves/spins the wrong way, or a display/sensor
doesn't respond, this is the file to fix — not the logic elsewhere.
"""

# ---------------------------------------------------------------------------
# I2C addresses
# ---------------------------------------------------------------------------
# These are the common factory-default addresses. Adeept's Motor HAT V2.0,
# the MPU6050, and a typical SSD1306 OLED all default to DIFFERENT addresses,
# so all three can share one I2C bus (Pi pins: SDA=GPIO2/pin3, SCL=GPIO3/pin5)
# wired in parallel — no address conflict expected.
#
# Verify with: sudo i2cdetect -y 1
# You should see three device addresses show up: 0x40, 0x68, 0x3c (typically).
PCA9685_ADDR = 0x40   # Adeept Motor HAT V2.0 (PCA9685 PWM driver)
MPU6050_ADDR = 0x68   # MPU6050 IMU
OLED_ADDR = 0x3C      # SSD1306-family OLED ("1107" - confirm your exact driver chip)

I2C_BUS = 1

# ---------------------------------------------------------------------------
# PCA9685 servo/motor channels
# ---------------------------------------------------------------------------
# CHECK THESE against the Adeept Motor HAT V2.0 manual (search "ADM057" on
# adeept.com/learn) or by testing one channel at a time — channel numbering
# is the single most common source of "wrong motor moved" bugs.

# DC drive motors (wheels) — Motor HAT V2.0 uses an L298P bridge whose
# speed (ENA/ENB) is set via two PCA9685 PWM channels, while direction is
# set via GPIO pins directly from the Pi header (NOT through the PCA9685).
MOTOR_LEFT_PWM_CHANNEL = 0
MOTOR_RIGHT_PWM_CHANNEL = 1

# BCM GPIO pin numbers for direction control (IN1/IN2/IN3/IN4 on the L298P).
# These are frequently GPIO 27/17 (left) and 22/23 (right) or similar on
# Adeept boards — CONFIRM against your board's silkscreen/manual before
# powering DC motors, since driving the wrong pins can cause a brief
# reversed-direction jolt but will not damage anything at logic-level GPIO.
MOTOR_LEFT_IN1 = 27
MOTOR_LEFT_IN2 = 17
MOTOR_RIGHT_IN1 = 22
MOTOR_RIGHT_IN2 = 23

# Expressive servos (head pan/tilt, ears, whatever you've mechanically built).
# Add/remove entries freely; channel numbers must not collide with the two
# motor PWM channels above.
SERVO_CHANNELS = {
    "head_pan": 4,
    "head_tilt": 5,
    "ear_left": 6,
    "ear_right": 7,
}

# Per-servo safe angle limits (degrees) — protects gear trains from over-travel.
SERVO_LIMITS = {
    "head_pan": (30, 150),
    "head_tilt": (60, 120),
    "ear_left": (0, 90),
    "ear_right": (0, 90),
}

SERVO_NEUTRAL = {
    "head_pan": 90,
    "head_tilt": 90,
    "ear_left": 45,
    "ear_right": 45,
}

SERVO_PWM_FREQ = 50  # standard analog servo frequency (Hz)

# ---------------------------------------------------------------------------
# OLED display
# ---------------------------------------------------------------------------
OLED_WIDTH = 128
OLED_HEIGHT = 64  # change to 32 if your module is the shorter 128x32 variant

# ---------------------------------------------------------------------------
# Voice / audio
# ---------------------------------------------------------------------------
WAKE_WORD = None  # e.g. "hey robot" — set to None to respond to any speech
LISTEN_TIMEOUT_S = 5
PHRASE_TIME_LIMIT_S = 6

# ---------------------------------------------------------------------------
# Behavior loop timing
# ---------------------------------------------------------------------------
BLINK_INTERVAL_RANGE_S = (3, 8)     # idle blink randomness
IMU_POLL_HZ = 20
SHAKE_ACCEL_THRESHOLD_G = 1.6       # combined accel magnitude that counts as "bumped/shaken"
TILT_ANGLE_THRESHOLD_DEG = 35       # pitch/roll that counts as "picked up / tipped"
