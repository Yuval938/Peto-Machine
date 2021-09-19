from IScheduler import IScheduler
from IPETO import IPETO
import schedule
import requests
import time


def check_for_new_schedule(peto):
    print("asking server if there is a new feeding schedule")
    schedule_list = requests.get(f'http://192.168.1.39:5000/meal/pet/{peto.id}').json()
    new_hash = hash(schedule_list)
    if new_hash == peto.scheduleHash:
        print("no new schedule found")
        pass
    else:
        print("updating schedule now")
        peto.hash = new_hash
        for meal in schedule_list:
            if meal['repeat_daily']:
                schedule.every().day.at(meal["time"]).do(feed, meal["amount"]).tag("normalRoutine", meal["id"])
            else:
                schedule.every().day.at(meal["time"]).do(feedOnce, peto, meal["amount"], meal["id"]).tag(
                    "normalRoutine", meal["id"])  # will be deleted from schedule after one feed
            print("meal added")


def should_I_Feed(peto):
    print("asking server if there's a feed request pending")
    val = requests.get(f'http://192.168.1.39:5000/pets/feed/{peto.id}').text.strip('\n')
    if val != 'null':
        grams = int(val)
        peto.FeedPet(grams=grams)
        schedule.every(1).minutes.do(check_for_remaining_food, peto)


def check_for_remaining_food(peto):
    print("checking remaining food on plate")
    latest = peto.GetCurrentPlateStatus()
    food_eaten = peto.foodOnPlate - latest
    delta = peto.latest - latest
    peto.latest = latest
    print(f"food on plate is {latest}")
    if delta <= 3 and food_eaten > 2:
        food_eaten = peto.foodOnPlate - peto.latest
        print(f"finished meal sending lunch status amount dog eat :{food_eaten}")
        return schedule.CancelJob


def feed(peto, grams):
    print("feeding pet")
    peto.FeedPet(grams)
    schedule.every(1).minutes.do(check_for_remaining_food, peto)


def feedOnce(peto, grams, job_id):
    print("feeding pet")
    peto.FeedPet(grams)
    schedule.every(1).minutes.do(check_for_remaining_food, peto)
    requests.delete(f'http://192.168.1.39:5000/meal/{job_id}')
    return schedule.CancelJob


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
        schedule.every(30).seconds.do(check_for_new_schedule)
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
