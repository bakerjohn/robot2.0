#!/usr/bin/env python3
"""
main.py — run this to bring the robot to life:  python3 main.py
Ctrl+C to stop cleanly (motors/servos will center and release).
"""

import time
from brain import Robot


def main():
    robot = Robot()
    robot.start()
    print("Robot running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        robot.shutdown()


if __name__ == "__main__":
    main()
