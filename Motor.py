from abc import ABC, abstractmethod
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)


class IMotor(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def motorOn(self):
        pass

    @abstractmethod
    def motorOff(self):
        pass


class Motor(IMotor):
    def __init__(self, servoControlPin: int):
        super().__init__()
        self.servoControlPin = servoControlPin
        try:
            # Here we are configuring our PIN to OUPUT to send current through it
            GPIO.setup(self.servoControlPin, GPIO.OUT)
            # Now we have to set the pulse wave modulations
            ''' 
            FULL SPEED FORWARD --> Position "180" requires 2ms pulse 
            FULL SPEED BACKWARD -->  Position "0" requires 1ms pulse 
            STOP --> Position "90" requires 1.5ms pulses
            PWM is a way to send some pulses to the control PIN of the servo.
            For example, a PWM at 1 Hertz means 1 pulse every second.
            '''

            self.PWM_FREQUENCY = 100  # In Hertz, which means 100 pulses in 1secs (1000ms) --> 1 pulse = 10ms

            '''
            However, 20ms pulses are still too long for FORWARD (2ms) or BACKWARD(1ms).
            Looking at the documentation of PWM we can also set duty cycle.
            We use the following calculation : DCPurcentage = ( ms_required / PWM_FRQ ) x 100 (to have a % between 0 and 100)
            for FORWARD : ( 2 / 10 ) X 100 = 20% of dutycycle.
            for BACKWARD : ( 1 / 10 ) X 100 = 10% of dutycycle.
            '''

            self.FULL_SPEED_FORWARD_DC = 18
            self.FULL_SPEED_BACKWARD_DC = 10
            self.pwm = GPIO.PWM(self.servoControlPin, self.PWM_FREQUENCY)
        except:
            print("something went wrong")

    def motorOn(self):
        self.pwm.start(self.FULL_SPEED_FORWARD_DC)
        time.sleep(0.3)
        self.pwm.ChangeDutyCycle(0)

    def motorOff(self):
        self.pwm.stop()
