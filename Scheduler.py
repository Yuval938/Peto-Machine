from IScheduler import IScheduler
from IPETO import IPETO
import schedule
import requests
import time


def check_for_new_schedule():
    print("asking server if there is a new feeding schedule")
    #if not in list we should add a job


def should_I_Feed(peto):
    print("asking server if there's a feed request pending")
    val = requests.get('http://192.168.1.39:5000/pets/feed/1').text.strip('\n')
    if val != 'null':
        grams = int(val)
        peto.FeedPet(grams=grams)
        schedule.every(1).minutes.do(check_for_remaining_food,peto)


def check_for_remaining_food(peto):
    print("checking remaining food on plate")
    val = peto.GetCurrentPlateStatus()
    delta = peto.latest - val
    peto.latest = val
    print(f"food on plate is {val}")
    if delta <=5:
        food_eaten = peto.foodOnPlate - peto.latest
        print(f"finished meal sending lunch status amount dog eat :{food_eaten}")
        return schedule.CancelJob



def feed(peto,grams):
    print("feeding pet")
    peto.FeedPet(grams)
    schedule.every(1).minutes.do(check_for_remaining_food, peto)


class Scheduler(IScheduler):
    def __init__(self, peto: IPETO):
        super().__init__(peto)
        self.peto = peto

    def remove_from_schedule(self, job):
        schedule.cancel_job(job)
        pass

    def add_to_schedule(self, func):
        pass

    def normalRoutine(self):
        # schedule.every(1).minutes.do(check_for_new_schedule)
        schedule.every(4).seconds.do(should_I_Feed, self.peto)
        # schedule.every(4).minutes.do(feed, self.peto,30)
        while 1:
            schedule.run_pending()
            time.sleep(1)
        # schedule.every().hour.do(job)
        # schedule.every().day.at("10:30").do(job)
        pass
    def BootupRoutine(self):
        pass
        # here we should try fetch info via Bluetooth from mobile phone in order to establish connection to local network
