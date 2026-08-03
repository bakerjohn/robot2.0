from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import Image, ImageDraw
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
# SETTINGS
# -----------------------------

pupil_x = 0
pupil_y = 0


# -----------------------------
# DRAW HELPERS
# -----------------------------

def new_image():
    return Image.new(
        "1",
        (WIDTH, HEIGHT)
    )


def display(image):
    device.display(image)



# -----------------------------
# COZMO EYES
# -----------------------------

def draw_eyes(
        px=0,
        py=0,
        eyelid=0
):

    image = new_image()
    draw = ImageDraw.Draw(image)


    # left eye
    draw.rounded_rectangle(
        (5,5,58,59),
        radius=18,
        fill=255
    )


    # right eye
    draw.rounded_rectangle(
        (70,5,123,59),
        radius=18,
        fill=255
    )


    # pupils

    draw.ellipse(
        (
            23+px,
            20+py,
            42+px,
            44+py
        ),
        fill=0
    )


    draw.ellipse(
        (
            88+px,
            20+py,
            107+px,
            44+py
        ),
        fill=0
    )


    # eyelids

    if eyelid > 0:

        draw.rectangle(
            (0,0,128,eyelid),
            fill=0
        )

        draw.rectangle(
            (0,64-eyelid,128,64),
            fill=0
        )


    display(image)



# -----------------------------
# ANIMATIONS
# -----------------------------

def blink():

    for lid in range(0,35,5):

        draw_eyes(
            pupil_x,
            pupil_y,
            lid
        )

        time.sleep(.03)


    for lid in range(35,0,-5):

        draw_eyes(
            pupil_x,
            pupil_y,
            lid
        )

        time.sleep(.03)



def look_around():

    global pupil_x

    positions = [
        -10,
        -6,
        0,
        6,
        10,
        6,
        0
    ]

    for pos in positions:

        pupil_x = pos

        draw_eyes(
            pupil_x,
            pupil_y
        )

        time.sleep(.12)



def happy():

    image = new_image()
    draw = ImageDraw.Draw(image)


    # smiling eyes

    draw.arc(
        (5,15,58,55),
        20,
        160,
        fill=255,
        width=3
    )

    draw.arc(
        (70,15,123,55),
        20,
        160,
        fill=255,
        width=3
    )


    display(image)

    time.sleep(2)



def curious():

    for y in [-5,-3,0]:

        draw_eyes(
            random.randint(-5,5),
            y
        )

        time.sleep(.2)



def surprised():

    image = new_image()
    draw = ImageDraw.Draw(image)


    draw.rounded_rectangle(
        (5,5,58,59),
        radius=20,
        fill=255
    )

    draw.rounded_rectangle(
        (70,5,123,59),
        radius=20,
        fill=255
    )


    # large pupils

    draw.ellipse(
        (20,15,45,48),
        fill=0
    )

    draw.ellipse(
        (85,15,110,48),
        fill=0
    )


    display(image)

    time.sleep(2)



def sleepy():

    image = new_image()
    draw = ImageDraw.Draw(image)


    draw.rectangle(
        (5,25,58,35),
        fill=255
    )

    draw.rectangle(
        (70,25,123,35),
        fill=255
    )


    display(image)



def thinking():

    for x in [-6,6,-6,6,0]:

        draw_eyes(
            x,
            0
        )

        time.sleep(.15)



# -----------------------------
# MAIN PERSONALITY LOOP
# -----------------------------

print("Cozmo eyes running")
print("CTRL+C to stop")


try:

    while True:


        # normal idle

        draw_eyes()

        time.sleep(2)


        # random personality

        action = random.choice(
            [
                "look",
                "blink",
                "happy",
                "curious",
                "think",
                "surprise"
            ]
        )


        if action == "look":
            look_around()


        elif action == "blink":
            blink()


        elif action == "happy":
            happy()


        elif action == "curious":
            curious()


        elif action == "think":
            thinking()


        elif action == "surprise":
            surprised()


        time.sleep(1)



except KeyboardInterrupt:

    print("Stopping...")

    image = new_image()

    display(image)
