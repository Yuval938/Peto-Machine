# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from time import sleep

from Motor import Motor
from PETO import PETO
from Scale import Scale
import RPi.GPIO as GPIO  # import GPIO
import requests

GPIO.setmode(GPIO.BCM)


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    plate_scale = Scale('swap_file.swp', 21, 20)
    plate_scale.initWeight()
    motor = Motor(18)
    peto = PETO(plate_scale, plate_scale, motor)
    try:
        peto.GetCurrentPlateStatus()
        # grams = input('Enter amount of food (in grams): ')
        while True:
            print('check')
            val = requests.get('http://10.0.0.9:5000/pets/feed/1').text.strip('\n')
            if val != 'null':
                grams = int(val)
                peto.FeedPet(grams=grams)
            sleep(3)
    # if plate_scale.initWeight():
    #     while True:
    #         plate_scale.weight()
    # print_hi('PyCharm')

    except (KeyboardInterrupt, SystemExit):
        print('Bye :)')

    finally:
        GPIO.cleanup()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
