#!/usr/bin/env python3
#100 LED RGB String Lights controlled with adafruit NeoPixel

from re import L
import time
from rpi_ws281x import *
import argparse
import sys
import math

# LED strip configuration:
LED_COUNT      = 100      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz
LED_DMA        = 10      # DMA channel to use for generating signal
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

#Define light functions here
def colorWipe(strip, color, wait_ms=50):
    #Wipe color across display a pixel at a time.
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def wheel(pos):
    #Generate rainbow colors across 0-255 positions.
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    #Draw rainbow that uniformly distributes itself across all pixels.
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbow(strip, wait_ms=20, iterations=1):
    #Draw rainbow that fades across all pixels at once.
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

#Sets a static umbre across all pixels
def fade(strip, col1, col2):
    c = col1
    rDiff = col2[0] - col1[0]
    gDiff = col2[1] - col1[1]
    bDiff = col2[2] - col1[2]
    for i in range(strip.numPixels()):
        c[0] += rDiff / strip.numPixels()
        c[1] += gDiff / strip.numPixels()
        c[2] += bDiff / strip.numPixels()
        strip.setPixelColor(i, Color(round(c[0]), round(c[1]), round(c[2])))
        print(c)
        strip.show()
        time.sleep(50/1000.0)

#Displays bisexual pride flag - June (2020 addition)
def bi(strip, wait_ms=50):
    for i in range((strip.numPixels() // 5) * 2):
        strip.setPixelColor(i, Color(230, 9, 90))
        strip.show()
        time.sleep(wait_ms/1000.0)
    for i in range(((strip.numPixels() // 5) * 2), (((strip.numPixels() // 5) * 2) + (strip.numPixels() // 5))):
        strip.setPixelColor(i, Color(150, 0, 156))
        strip.show()
        time.sleep(wait_ms/1000.0)
    for i in range(((strip.numPixels() // 5) * 3), strip.numPixels()):
        strip.setPixelColor(i, Color(0, 100, 200))
        strip.show()
        time.sleep(wait_ms/1000.0)

#Converts input string into colour
def convStringColour(input):
    if input == "purple":
        return [150, 0, 139]
    if input == "magenta":
        return [255, 0, 190]
    if input == "teal":
        return [0, 128, 128]
    if input == "red":
        return [255, 0, 0]
    if input == "peach":
        return [249, 68, 86]
    if input == "pink":
        return [255, 20, 147]
    if input == "orange":
        return [225, 45, 0]
    if input == "a":
        return [156, 45, 0]
    else:
        listNum = input.split(',')
        try:
            return [int(listNum[0]), int(listNum[1]), int(listNum[2])]
        except IndexError:
            return [156, 45, 0]


if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    #Create group to process data for strip
    variables = parser.add_argument_group('Variables', 'Adjust values such as brightness and pin')
    variables.add_argument('-b', '--brightness', action='store', dest='b', type=int, default=255, help='Adjust the brightness of the lights')
    variables.add_argument('-o', '--colour', action='store', dest='o', default="purple", help='Colour argument to be used with -s or -f(will be first colour in f), specified in 0,0,0(RGB no space) or "purple"(words)')
    variables.add_argument('-p', '--colourp', action='store', dest='p', default="purple", help='Colour argument to be used with -f(will be second colour in f), specified in 0,0,0(RGB no space) or "purple"(words)')
    variables.add_argument('-l',  '--leds', action = 'store', dest='l', type=int, default = 100, help = 'Adjust number of LEDs to light up, helpful for dodgy power supplies')
    #Create mutually exclusive group to process lights mode
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('-a', '--aesthetic', action='store_true', dest='a', help='Classic aesthetic warm orange string lights')
    mode.add_argument('-r', '--rainbow', action='store_true', dest='r',  help='Rainbow synced across all lights')
    mode.add_argument('-c', '--rainbowCycle', action='store_true', dest='rC',  help='Rainbow gradient across all lights')
    mode.add_argument('-s', '--singleColour', action='store_true', dest='s', help='Sets a single colour across all lights must be used with the -o(colour) argument')
    mode.add_argument('-f', '--fade', action='store_true', dest='f', help='Sets a static fade across all pixels, must be used with -o and -p')
    mode.add_argument('-g', '--bi', action='store_true', dest='g', help='Sets lights to bi pride colours :)')
    args = parser.parse_args()

    LIGHTS_MODE = ""
    if args.a:
        LIGHTS_MODE = "aesthetic"
    elif args.r:
        LIGHTS_MODE = "rainbow"
    elif args.rC:
        LIGHTS_MODE = "rainbowCycle"
    elif args.s:
        LIGHTS_MODE = "static"
    elif args.f:
        LIGHTS_MODE = "fade"
    elif args.g:
        LIGHTS_MODE = "bi"

    c1 = convStringColour(args.o)
    c2 = convStringColour(args.p)


    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(args.l, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, args.b, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    #User friendly stuff
    #Clear.sh works to kill it in the background if it's your only script running
    print ('Press Ctrl+C to exit')
    #Main loop
    RUNNING = True
    try:
        while RUNNING:
            #Check mode and run relevant loop
            if LIGHTS_MODE == "rainbow":
                rainbow(strip)
            elif LIGHTS_MODE == "aesthetic":
                colorWipe(strip, Color(156, 45, 0))
            elif LIGHTS_MODE == "rainbowCycle":
                rainbowCycle(strip)
            elif LIGHTS_MODE == "static":
                colorWipe(strip, Color(c1[0], c1[1], c1[2]))
            elif LIGHTS_MODE == "fade":
                fade(strip, c1, c2)
                LIGHTS_MODE = "HELP"
            elif LIGHTS_MODE == "bi":
                bi(strip)
            elif LIGHTS_MODE == "HELP":
                time.sleep(1)
            else:
                print("No mode selected, exiting...")
                sys.exit()
    except KeyboardInterrupt:
        #On program end/kill(-INT) clear lights
        colorWipe(strip, Color(0,0,0), 10)
