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
    config.read('cfg.ini')  # init config with args
    plate_scale = Scale(config['SCALE']['plate_scale_cfg'], 11, 10)  # init scale
    plate_scale.initWeight()  # loac cfg
    container_scale = Scale(config['SCALE']['container_scale_cfg'], 21, 20)  # init second scale
    container_scale.initWeight()  # load cfg
    motor = Motor(18)  # init motor
    lamp = Lamp(12)  # init lamp
    # init PETO with sensors(lamp,motor,scale) as args
    peto = PETO(plateScale=plate_scale, containerScale=container_scale, motor=motor,
                lamp=lamp, machine_id=int(config['PETO']['machine_id']))
    # init Scheduler with PETO as arg
    petoSchudeler = Scheduler(peto=peto, config=config)
    try:
        while True:
            # preform the predefined schedule
            petoSchudeler.normalRoutine()
    except (KeyboardInterrupt, SystemExit):
        print('Bye :)')
    finally:
        peto.lamp.MachineOn = False
        GPIO.cleanup()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
