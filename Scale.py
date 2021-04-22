from IScale import IScale
from sensors.HX711.hx711 import HX711
import RPi.GPIO as GPIO  # import GPIO
import pickle
import os


class Scale(IScale):
    def __init__(self, cfg_file_name: str,dout_pin:int,dout_sck_pin:int):
        self.cfg_file_name = cfg_file_name  # this will detrmine which scale we are addressing to
        # self.dout_pin=dout_pin
        # self.dout_sck_pin=dout_sck_pin
        # # Create an object hx which represents your real hx711 chip
        # # Required input parameters are only 'dout_pin' and 'pd_sck_pin'
        self.hx = HX711(self.dout_pin,self.dout_sck_pin)
        pass

    def weight(self):
        WeightInFloat = self.hx.get_weight_mean(20)
        print(WeightInFloat, 'g')
        return int(WeightInFloat)
        pass

    def initWeight(self):
        GPIO.setmode(GPIO.BCM)  # set GPIO pin mode to BCM numbering
        # Create an object hx which represents your real hx711 chip
        # Required input parameters are only 'dout_pin' and 'pd_sck_pin'
        self.hx = HX711(dout_pin=21, pd_sck_pin=20)
        # Check if we have swap file. If yes that suggest that the program was not
        # terminated proprly (power failure). We load the latest state.
        self.cfg_file_name = 'swap_file.swp'
        if os.path.isfile(self.cfg_file_name):
            with open(self.cfg_file_name, 'rb') as swap_file:
                self.hx = pickle.load(swap_file)
                return True
                # now we loaded the state before the Pi restarted.
        else:
            print("no such .swp file")
            return False