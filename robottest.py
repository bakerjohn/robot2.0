from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import Image, ImageDraw
import sounddevice as sd
import numpy as np
import time
import random


# -----------------------------
# OLED SETUP
# -----------------------------

serial = i2c(
    port=1,
    address=0x3C
)

device = sh1106(serial)

WIDTH = 128
HEIGHT = 64


# -----------------------------
# AUDIO SETUP
# -----------------------------

MIC_DEVICE = 1   # USB microphone

volume_level = 0


def audio_callback(indata, frames, time_info, status):

    global volume_level

    volume = np.linalg.norm(indata) * 10

    # smooth volume
    volume_level = (
        volume_level * 0.8 +
        volume * 0.2
    )


mic = sd.InputStream(
    device=MIC_DEVICE,
    channels=1,
    callback=audio_callback
)

mic.start()


# -----------------------------
# DRAW FUNCTIONS
# -----------------------------

def blank():
    image = Image.new(
        "1",
        (WIDTH, HEIGHT)
    )

    return image, ImageDraw.Draw(image)



def normal(pupil_x=0):

    image, draw = blank()

    # eyes
    draw.rounded_rectangle(
        (8,12,56,52),
        radius=12,
        outline=255,
        width=2
    )

    draw.rounded_rectangle(
        (72,12,120,52),
        radius=12,
        outline=255,
        width=2
    )


    # pupils
    draw.ellipse(
        (25+pupil_x,25,38+pupil_x,38),
        fill=255
    )

    draw.ellipse(
        (89+pupil_x,25,102+pupil_x,38),
        fill=255
    )

    device.display(image)



def happy():

    image, draw = blank()

    draw.arc(
        (8,15,56,55),
        20,
        160,
        fill=255,
        width=3
    )

    draw.arc(
        (72,15,120,55),
        20,
        160,
        fill=255,
        width=3
    )

    device.display(image)



def sleepy():

    image, draw = blank()

    draw.line(
        (10,32,55,32),
        fill=255,
        width=3
    )

    draw.line(
        (73,32,118,32),
        fill=255,
        width=3
    )

    device.display(image)



def surprised():

    image, draw = blank()

    draw.ellipse(
        (8,8,56,56),
        outline=255,
        width=2
    )

    draw.ellipse(
        (72,8,120,56),
        outline=255,
        width=2
    )


    draw.ellipse(
        (25,20,40,42),
        fill=255
    )

    draw.ellipse(
        (89,20,104,42),
        fill=255
    )

    device.display(image)



def angry():

    image, draw = blank()

    draw.rounded_rectangle(
        (8,12,56,52),
        radius=10,
        outline=255,
        width=2
    )

    draw.rounded_rectangle(
        (72,12,120,52),
        radius=10,
        outline=255,
        width=2
    )


    # eyebrows

    draw.line(
        (8,10,55,22),
        fill=255,
        width=3
    )

    draw.line(
        (73,22,120,10),
        fill=255,
        width=3
    )


    draw.ellipse(
        (25,27,38,40),
        fill=255
    )

    draw.ellipse(
        (89,27,102,40),
        fill=255
    )


    device.display(image)



def blink():

    for height in [20,15,10,5,2]:

        image, draw = blank()

        draw.rounded_rectangle(
            (10,32-height//2,54,32+height//2),
            radius=4,
            fill=255
        )

        draw.rounded_rectangle(
            (74,32-height//2,118,32+height//2),
            radius=4,
            fill=255
        )

        device.display(image)

        time.sleep(.03)


    time.sleep(.1)


# -----------------------------
# MAIN LOOP
# -----------------------------

print("Robot eyes running")
print("Press CTRL+C to stop")


last_blink = time.time()


try:

    while True:


        # automatic blinking

        if time.time() - last_blink > random.randint(3,7):

            blink()
            last_blink = time.time()



        # sound reaction

        if volume_level < 0.3:

            sleepy()


        elif volume_level < 2:

            # idle movement

            for x in [-4,-2,0,2,4,2,0]:

                normal(x)
                time.sleep(.05)



        elif volume_level < 5:

            happy()



        else:

            surprised()



        time.sleep(.05)



except KeyboardInterrupt:

    print("\nStopping robot eyes")

    mic.stop()
    mic.close()

    image = Image.new(
        "1",
        (WIDTH,HEIGHT)
    )

    device.display(image)
