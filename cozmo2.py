from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import Image, ImageDraw
import time
import random


# OLED

serial = i2c(
    port=1,
    address=0x3C
)

device = sh1106(serial)


WIDTH = 128
HEIGHT = 64



def image():

    return Image.new(
        "1",
        (WIDTH, HEIGHT)
    )



def show(img):

    device.display(img)



# -------------------------
# COZMO EYES
# -------------------------


def idle(width=42,height=50,offset=0):

    img=image()
    draw=ImageDraw.Draw(img)


    # left eye

    draw.rounded_rectangle(
        (
            8+offset,
            7,
            8+width+offset,
            7+height
        ),
        radius=15,
        fill=255
    )


    # right eye

    draw.rounded_rectangle(
        (
            78+offset,
            7,
            78+width+offset,
            7+height
        ),
        radius=15,
        fill=255
    )


    show(img)



def happy():

    img=image()
    draw=ImageDraw.Draw(img)


    # smiling eyes

    draw.arc(
        (8,15,55,55),
        200,
        340,
        fill=255,
        width=4
    )


    draw.arc(
        (73,15,120,55),
        200,
        340,
        fill=255,
        width=4
    )


    show(img)



def angry():

    img=image()
    draw=ImageDraw.Draw(img)


    # slanted eyes

    draw.polygon(
        [
            (8,18),
            (55,8),
            (55,45),
            (8,55)
        ],
        fill=255
    )


    draw.polygon(
        [
            (73,8),
            (120,18),
            (120,55),
            (73,45)
        ],
        fill=255
    )


    show(img)



def surprised():

    img=image()
    draw=ImageDraw.Draw(img)


    draw.ellipse(
        (8,5,55,59),
        fill=255
    )


    draw.ellipse(
        (73,5,120,59),
        fill=255
    )


    show(img)



def sleepy():

    img=image()
    draw=ImageDraw.Draw(img)


    draw.rounded_rectangle(
        (8,28,55,38),
        radius=5,
        fill=255
    )


    draw.rounded_rectangle(
        (73,28,120,38),
        radius=5,
        fill=255
    )


    show(img)



def blink():

    for size in range(55,5,-5):

        img=image()
        draw=ImageDraw.Draw(img)


        y=32-(size//2)


        draw.rounded_rectangle(
            (8,y,55,y+size),
            radius=8,
            fill=255
        )


        draw.rounded_rectangle(
            (73,y,120,y+size),
            radius=8,
            fill=255
        )


        show(img)

        time.sleep(.03)



def look():

    for move in [-5,-3,0,3,5,3,0]:

        idle(
            offset=move
        )

        time.sleep(.1)



# -------------------------
# PERSONALITY LOOP
# -------------------------


print("Cozmo style eyes running")

try:

    while True:


        idle()

        time.sleep(2)


        action=random.choice(
            [
                "blink",
                "look",
                "happy",
                "sleep",
                "surprise",
                "angry"
            ]
        )


        if action=="blink":
            blink()

        elif action=="look":
            look()

        elif action=="happy":
            happy()

        elif action=="sleep":
            sleepy()

        elif action=="surprise":
            surprised()

        elif action=="angry":
            angry()


        time.sleep(1)



except KeyboardInterrupt:

    print("Stopping")

    show(image())
