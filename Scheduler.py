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
    print(f"food on plate is {val}")
    if peto.latest <= val or peto.latest >= val + 10:
        print("finished meal sending lunch status")
        return schedule.CancelJob
    peto.latest = val



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
        schedule.every(1).minutes.do(check_for_new_schedule)
        schedule.every(4).seconds.do(should_I_Feed, self.peto)
        schedule.every(4).minutes.do(feed, self.peto,30)
        while 1:
            schedule.run_pending()
            time.sleep(1)
        # schedule.every().hour.do(job)
        # schedule.every().day.at("10:30").do(job)
        pass
    def BootupRoutine(self):
        # here we should try fetch info via Bluetooth from mobile phone in order to establish connection to local network
