"""
imu_sensor.py — polls the MPU6050 and raises simple events ("shaken",
"tilted", "level") that the behavior layer can react to, similar to how
Coglet's roadmap talks about sensing being picked up or bumped.
"""

import math
import time
import threading

import smbus2

import config

# MPU6050 registers
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43


class MPU6050:
    def __init__(self, bus_num=None, address=None):
        self.bus = smbus2.SMBus(bus_num or config.I2C_BUS)
        self.addr = address or config.MPU6050_ADDR
        # wake the sensor up (it starts in sleep mode)
        self.bus.write_byte_data(self.addr, PWR_MGMT_1, 0)

    def _read_word(self, reg):
        high = self.bus.read_byte_data(self.addr, reg)
        low = self.bus.read_byte_data(self.addr, reg + 1)
        val = (high << 8) + low
        if val >= 0x8000:
            val = -((65535 - val) + 1)
        return val

    def read_accel_g(self):
        # +/-2g range default -> 16384 LSB/g
        x = self._read_word(ACCEL_XOUT_H) / 16384.0
        y = self._read_word(ACCEL_XOUT_H + 2) / 16384.0
        z = self._read_word(ACCEL_XOUT_H + 4) / 16384.0
        return x, y, z

    def read_gyro_dps(self):
        # +/-250 dps range default -> 131 LSB/(deg/s)
        x = self._read_word(GYRO_XOUT_H) / 131.0
        y = self._read_word(GYRO_XOUT_H + 2) / 131.0
        z = self._read_word(GYRO_XOUT_H + 4) / 131.0
        return x, y, z

    def read_tilt_deg(self):
        x, y, z = self.read_accel_g()
        pitch = math.degrees(math.atan2(x, math.sqrt(y * y + z * z)))
        roll = math.degrees(math.atan2(y, math.sqrt(x * x + z * z)))
        return pitch, roll


class MotionMonitor:
    """Background poller that calls on_shake()/on_tilt()/on_level() callbacks."""

    def __init__(self, on_shake=None, on_tilt=None, on_level=None):
        self.imu = MPU6050()
        self.on_shake = on_shake or (lambda: None)
        self.on_tilt = on_tilt or (lambda: None)
        self.on_level = on_level or (lambda: None)
        self._stop = threading.Event()
        self._was_tilted = False
        self._thread = threading.Thread(target=self._loop, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _loop(self):
        period = 1.0 / config.IMU_POLL_HZ
        while not self._stop.is_set():
            try:
                x, y, z = self.imu.read_accel_g()
                magnitude = math.sqrt(x * x + y * y + z * z)
                pitch, roll = self.imu.read_tilt_deg()

                if abs(magnitude - 1.0) > (config.SHAKE_ACCEL_THRESHOLD_G - 1.0):
                    self.on_shake()

                tilted = (abs(pitch) > config.TILT_ANGLE_THRESHOLD_DEG
                          or abs(roll) > config.TILT_ANGLE_THRESHOLD_DEG)
                if tilted and not self._was_tilted:
                    self.on_tilt()
                elif not tilted and self._was_tilted:
                    self.on_level()
                self._was_tilted = tilted
            except OSError:
                pass  # transient I2C hiccup - skip this sample
            time.sleep(period)


if __name__ == "__main__":
    m = MPU6050()
    while True:
        print("accel(g):", m.read_accel_g(), "tilt(deg):", m.read_tilt_deg())
        time.sleep(0.2)
