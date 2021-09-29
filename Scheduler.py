from IScheduler import IScheduler
from IPETO import IPETO
import schedule
import requests
import time
from datetime import datetime
import json
from Meal import Meal

serverURL: int = None
serverPORT: int = None
min_scale_val: int = None
max_scale_val: int = None


def bootupRoutine(peto):
    peto.Blink()
    while True:
        print("finding pair")
        time.sleep(3)
        try:
            # find if machine id allocated to a pet_id
            result = requests.get(f'{serverURL}:{serverPORT}/pair/{peto.machine_id}').json()['pet_id']
            print(result)
            if result:  # if not,we can pair, else - we try again.
                peto.id = result
                # lets find pet's name
                peto.petName = requests.get(f'{serverURL}:{serverPORT}/pets/{result}').json()['name']
                print("found!")
                peto.Blink()
                peto.lightON()
                break

        except:
            print("failed")
    peto.lightON()
    return schedule.CancelJob  # no need to keep pairing once paired.


def container_status(peto):
    # get current amount of food in container and update server.
    # we want to avoid "bad" math so we elimnate any reading that is above 1000 or less than 100
    val = peto.GetCurrentContainer()
    if val < min_scale_val:
        val = 0  # min value posible
    elif val > max_scale_val:
        val = max_scale_val  # max value possible
    percentage = val / max_scale_val
    response = requests.post(f'{serverURL}:{serverPORT}/pets/feed/{peto.id}', data={
        "container": percentage
    })
    return percentage
    # for debug
    # print(peto.GetCurrentContainer())
    # print(peto.GetCurrentPlateStatus())


# asking server if there is a new feeding schedule, If so, we add it to the schedule .
# if this is a one time meal we should delete it right after completion
def check_for_new_schedule(peto):
    print("asking server if there is a new feeding schedule")
    response = requests.get(f'{serverURL}:{serverPORT}/meal/pet/{peto.id}')
    if response.status_code == 200:
        schedule_list = response.json()
        new_hash = hash(str(schedule_list))
        if new_hash == peto.scheduleHash:  # if this is the same hash there is nothing new in the
            #    schedule we got from the server no need to update
            print("no new schedule found")
            pass
        else:
            print("updating schedule now")
            schedule.clear('schedule')
            peto.scheduleHash = new_hash
            for meal in schedule_list:
                if meal['repeat_daily']:
                    schedule.every().day.at(meal["time"]).do(feed, peto, meal["amount"], meal["id"], meal["name"]).tag(
                        "normalRoutine", meal["id"])
                else:
                    schedule.every().day.at(meal["time"]).do(feedOnce, peto, meal["amount"], meal["id"],
                                                             meal["name"]).tag(
                        "normalRoutine", meal["id"])  # will be deleted from schedule after one feed
                print("meal added")


# asking server if there's an instant feed request pending
def should_I_Feed(peto):
    print("asking server if there's a feed request pending")
    val = requests.get(f'{serverURL}:{serverPORT}/pets/feed/{peto.id}').text.strip('\n')
    if val == 'null':
        pass
    elif int(val) == 0:  # if we got a 0 that means we are not paired to a pet_id , going back to pair mode.
        print("canceling jobs")
        schedule.clear('normalRoutine')
        # cancel jobs
    else:
        grams = int(val)
        num = peto.FeedPet(grams=grams)
        peto.currentMeal = Meal(name="instant Feed", mealTime=datetime.now().replace(microsecond=0), amountGiven=grams)
        # we update server that the meal was served
        x = requests.put(f'{serverURL}:{serverPORT}/push/{peto.id}', data={
            "title": "Meal Is Served!",
            "body": f"{num} grams added to plate"
        })
        # this is for meal follow up
        schedule.every(1).minutes.do(check_for_remaining_food, peto).tag("normalRoutine")


def check_for_remaining_food(peto):
    print("checking remaining food on plate")
    latest = peto.GetCurrentPlateStatus()
    startOfMealDelta = peto.foodOnPlate - latest  # amount eaten since meal was served
    delta = peto.latest - latest  # amount eaten since the last time we check
    peto.latest = latest
    print(f"food on plate is {latest}")
    # if the start of meal delta is larger than 2 and
    # we havent concluded that the pet stated eating - we can conclude that she started eating now!
    if startOfMealDelta > 2 and not peto.currentMeal.startedEating:
        peto.currentMeal.startedEating = True  # pet started eating.
        # peto.currentMeal.petStartedEating = datetime.now().strftime("%H:%M:%S")
        peto.currentMeal.petStartedEating = datetime.now().time().replace(
            microsecond=0)  # we document the time she started eating for later use.
    # the amount on plate hasn't changed much since last checked - pet finished eating!
    elif delta <= 3 and peto.currentMeal.startedEating:
        # amount of food on plate when started eating minus the current amount of food on plate = food eaten.
        food_eaten = peto.foodOnPlate - peto.latest
        # we document the time she finished eating for later use.
        peto.currentMeal.petFinishedEating = datetime.now().time().replace(microsecond=0)
        peto.currentMeal.amountEaten = food_eaten
        # we send meal summary as a push notification
        requests.put(f'{serverURL}:{serverPORT}/push/{peto.id}', data={
            "title": "Finished Eating!",
            "body": f"{peto.petName} ate {food_eaten} grams"
        })
        peto.currentMeal.startedEating = False
        # add to DB
        try:
            # we request server to add meal summary to DB
            x = requests.post(f'{serverURL}:{serverPORT}/meal/pet/{peto.id}',
                              data=json.loads(json.dumps(peto.currentMeal.__dict__, default=str)))
            print(x.text)
        except Error as error:
            print(error.msg)

        # print(f"finished meal sending lunch status amount dog eat :{food_eaten}")
        return schedule.CancelJob  # finished eating so no need to keep on checking.


def feed(peto, grams, mealID, mealName):
    # documenting meal in object
    peto.currentMeal = Meal(name=mealName, mealTime=datetime.now(), amountGiven=grams)
    print("feeding pet")
    num = peto.FeedPet(grams)
    # follow up for meal summary.
    schedule.every(1).minutes.do(check_for_remaining_food, peto).tag("normalRoutine")
    x = requests.put(f'{serverURL}:{serverPORT}/push/{peto.id}', data={
        "title": "Meal Is Served!",
        "body": f"{num} grams added to plate"
    })
    print(x)


# this is for non-repeat meals
# the name of the meal will be "instant feeding"
def feedOnce(peto, grams, mealID, mealName):
    print("feeding pet")
    peto.currentMeal = Meal(name=mealName, mealTime=datetime.now(), amountGiven=grams)
    #
    # peto.currentMeal.ID = mealID
    # peto.currentMeal.name = mealName
    # peto.currentMeal.mealTime = datetime.now().strftime("%H:%M:%S")
    num = peto.FeedPet(grams)
    # follow up for meal summary.
    schedule.every(1).minutes.do(check_for_remaining_food, peto).tag("normalRoutine")
    # push notification -  meal is served.
    x = requests.put(f'{serverURL}:{serverPORT}/push/{peto.id}', data={
        "title": "Meal Is Served!",
        "body": f"{num} grams added to plate"
    })
    # this is a one time meal so we need to tell server to delete it once we fed the pet.
    requests.delete(f'{serverURL}:{serverPORT}/meal/{mealID}')
    return schedule.CancelJob


class Scheduler(IScheduler):
    def __init__(self, peto: IPETO, config):
        super().__init__(peto)
        self.peto = peto
        self.config = config
        globals()['serverURL'] = config['DEFAULT']['server_url']
        globals()['serverPORT'] = config['DEFAULT']['server_port']
        globals()['min_scale_val'] = config.getint('SCALE', 'min_scale_val')
        globals()['max_scale_val'] = config.getint('SCALE', 'max_scale_val')

    def normalRoutine(self):
        self.peto.lightON()
        schedule.every(1).seconds.do(bootupRoutine, self.peto).tag("normalRoutine")
        schedule.every(5).seconds.do(container_status, self.peto).tag("normalRoutine")  # should be 10 min
        schedule.every(30).seconds.do(check_for_new_schedule, self.peto).tag("normalRoutine")
        schedule.every(4).seconds.do(should_I_Feed, self.peto).tag("normalRoutine")
        # schedule.every(4).minutes.do(feed, self.peto,30)
        while len(schedule.jobs) != 0:
            schedule.run_pending()
            time.sleep(1)
