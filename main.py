from Lamp import Lamp
from Motor import Motor
import configparser
from PETO import PETO
from Scale import Scale
import RPi.GPIO as GPIO  # import GPIO
import requests
from IScheduler import IScheduler
from Scheduler import Scheduler


GPIO.setmode(GPIO.BCM)

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('cfg.ini')
    plate_scale = Scale(config['DEFAULT']['plate_scale_cfg'], 11, 10)
    plate_scale.initWeight()
    container_scale = Scale(config['DEFAULT']['container_scale_cfg'], 21, 20)
    container_scale.initWeight()
    motor = Motor(18)
    lamp = Lamp(12)
    peto = PETO(plateScale=plate_scale, containerScale=container_scale, motor=motor,lamp=lamp)
    #if everything is ok,we should run the normal rotuine
    petoSchudeler = Scheduler(peto=peto)
    try:
        petoSchudeler.bootupRoutine()
        petoSchudeler.normalRoutine()
    except (KeyboardInterrupt, SystemExit):
        print('Bye :)')
    finally:
        GPIO.cleanup()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
