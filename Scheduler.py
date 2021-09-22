from IScheduler import IScheduler
from IPETO import IPETO
import schedule
import requests
import time
from datetime import datetime
import json
from Meal import Meal

mealIDtoName = dict


def check_for_new_schedule(peto):
    print("asking server if there is a new feeding schedule")
    schedule_list = requests.get(f'http://40.76.233.140:5000/meal/pet/{peto.id}').json()
    new_hash = hash(str(schedule_list))
    if new_hash == peto.scheduleHash:
        print("no new schedule found")
        pass
    else:
        print("updating schedule now")
        schedule.clear('schedule')
        peto.scheduleHash = new_hash
        for meal in schedule_list:
            if meal['repeat_daily']:
                schedule.every().day.at(meal["time"]).do(feed, peto, meal["amount"], meal["id"], meal["name"]).tag(
                    "schedule", meal["id"])
            else:
                schedule.every().day.at(meal["time"]).do(feedOnce, peto, meal["amount"], meal["id"], meal["name"]).tag(
                    "schedule", meal["id"])  # will be deleted from schedule after one feed
            print("meal added")


def should_I_Feed(peto):
    print("asking server if there's a feed request pending")
    val = requests.get(f'http://40.76.233.140:5000/pets/feed/{peto.id}').text.strip('\n')
    if val != 'null':
        grams = int(val)
        num = peto.FeedPet(grams=grams)
        peto.currentMeal = Meal(name="instant Feed",mealTime=datetime.now().replace(microsecond=0), amountGiven=grams)
        x = requests.put(f'http://40.76.233.140:5000/push/{peto.id}', data={
            "title": "Meal Is Served!",
            "body": f"{num} grams added to plate"
        })
        schedule.every(1).minutes.do(check_for_remaining_food, peto)


def check_for_remaining_food(peto):
    print("checking remaining food on plate")
    startedEating = False
    latest = peto.GetCurrentPlateStatus()
    startOfMealDelta = peto.foodOnPlate - latest
    delta = peto.latest - latest
    peto.latest = latest
    print(f"food on plate is {latest}")
    if startOfMealDelta > 2 and not startedEating:
        startedEating = True
        # peto.currentMeal.petStartedEating = datetime.now().strftime("%H:%M:%S")
        peto.currentMeal.petStartedEating = datetime.now().time().replace(microsecond=0)
        # dog started eating - mark the time
    if delta <= 3 and startedEating:
        food_eaten = peto.foodOnPlate - peto.latest  # amount of food on plate when started eating minus the current amount of food on plate = food eaten.
        # peto.currentMeal.petFinishedEating = datetime.now().strftime("%H:%M:%S")
        peto.currentMeal.petFinishedEating = datetime.now().time().replace(microsecond=0)
        peto.currentMeal.amountEaten = food_eaten
        requests.put(f'http://40.76.233.140:5000/push/{peto.id}', data={
            "title": "Finished Eating!",
            "body": f"{peto.petName} ate {food_eaten} grams"
        })
        # add to DB
        requests.post(f'http://40.76.233.140:5000/meal/pet/{peto.id}',
                          data=json.loads(json.dumps(peto.currentMeal.__dict__, default=str)))

        # print(f"finished meal sending lunch status amount dog eat :{food_eaten}")
        return schedule.CancelJob


def feed(peto, grams, mealID, mealName):
    peto.currentMeal = Meal(pet_id=peto.id, name=mealName, mealTime=datetime.now(),amountGiven=grams)
    # peto.currentMeal.ID = mealID
    # peto.currentMeal.name = mealName
    # peto.currentMeal.mealTime = datetime.now().strftime("%H:%M:%S")
    print("feeding pet")
    num = peto.FeedPet(grams)
    schedule.every(1).minutes.do(check_for_remaining_food, peto)
    x = requests.put(f'http://40.76.233.140:5000/push/{peto.id}', data={
        "title": "Meal Is Served!",
        "body": f"{num} grams added to plate"
    })
    print(x)


def feedOnce(peto, grams, mealID, mealName):
    print("feeding pet")
    peto.currentMeal = Meal(pet_id=peto.id, name=mealName, mealTime=datetime.now(),amountGiven=grams)
    #
    # peto.currentMeal.ID = mealID
    # peto.currentMeal.name = mealName
    # peto.currentMeal.mealTime = datetime.now().strftime("%H:%M:%S")
    num = peto.FeedPet(grams)
    schedule.every(1).minutes.do(check_for_remaining_food, peto)
    x = requests.put(f'http://40.76.233.140:5000/push/{peto.id}', data={
        "title": "Meal Is Served!",
        "body": f"{num} grams added to plate"
    })
    requests.delete(f'http://40.76.233.140:5000/meal/{mealID}')
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
        schedule.every(30).seconds.do(check_for_new_schedule, self.peto).tag("normalRoutine")
        schedule.every(4).seconds.do(should_I_Feed, self.peto).tag("normalRoutine")
        # schedule.every(4).minutes.do(feed, self.peto,30)
        while 1:
            schedule.run_pending()
            time.sleep(1)
        # schedule.every().hour.do(job)
        # schedule.every().day.at("10:30").do(job)
        pass

    def BootupRoutine(self):
        pass
        # we give server our serial code and wait for sync with mobile device
