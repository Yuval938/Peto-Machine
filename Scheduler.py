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
            result = requests.get(f'{serverURL}:{serverPORT}/pair/{peto.machine_id}').json()['pet_id']
            print(result)
            if result:
                peto.id = result
                # lets find pet's name
                peto.petName = requests.get(f'{serverURL}:{serverPORT}/pets/{result}').json()['name']
                print("found!")
                peto.Blink()
                peto.lightON()
                break

        except:
            print("failed")
    return schedule.CancelJob


def container_status(peto):
    val = peto.GetCurrentContainer()
    if val < min_scale_val:
        val = 0
    elif val > max_scale_val:
        val = max_scale_val
    percentage = val / max_scale_val
    response = requests.post(f'{serverURL}:{serverPORT}/pets/feed/{peto.id}', data={
        "container": percentage
    })
    return percentage

    print(peto.GetCurrentContainer())
    print(peto.GetCurrentPlateStatus())


def check_for_new_schedule(peto):
    print("asking server if there is a new feeding schedule")
    response = requests.get(f'{serverURL}:{serverPORT}/meal/pet/{peto.id}')
    if response.status_code == 200:
        schedule_list = response.json()
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
                    schedule.every().day.at(meal["time"]).do(feedOnce, peto, meal["amount"], meal["id"],
                                                             meal["name"]).tag(
                        "schedule", meal["id"])  # will be deleted from schedule after one feed
                print("meal added")


def should_I_Feed(peto):
    print("asking server if there's a feed request pending")
    val = requests.get(f'{serverURL}:{serverPORT}/pets/feed/{peto.id}').text.strip('\n')
    if val == 'null':
        pass
    elif int(val) == 0:
        print("canceling jobs")
        schedule.clear('normalRoutine')
        #cancel jobs
    else:
        grams = int(val)
        num = peto.FeedPet(grams=grams)
        peto.currentMeal = Meal(name="instant Feed", mealTime=datetime.now().replace(microsecond=0), amountGiven=grams)
        x = requests.put(f'{serverURL}:{serverPORT}/push/{peto.id}', data={
            "title": "Meal Is Served!",
            "body": f"{num} grams added to plate"
        })
        # schedule.every(15).seconds.do(check_for_remaining_food, peto)
        schedule.every(1).minutes.do(check_for_remaining_food, peto)



def check_for_remaining_food(peto):
    print("checking remaining food on plate")
    latest = peto.GetCurrentPlateStatus()
    startOfMealDelta = peto.foodOnPlate - latest
    delta = peto.latest - latest
    peto.latest = latest
    print(f"food on plate is {latest}")
    if startOfMealDelta > 2 and not peto.currentMeal.startedEating:
        peto.currentMeal.startedEating = True
        # peto.currentMeal.petStartedEating = datetime.now().strftime("%H:%M:%S")
        peto.currentMeal.petStartedEating = datetime.now().time().replace(microsecond=0)
        # dog started eating - mark the time
    elif delta <= 3 and peto.currentMeal.startedEating:
        food_eaten = peto.foodOnPlate - peto.latest  # amount of food on plate when started eating minus the current amount of food on plate = food eaten.
        # peto.currentMeal.petFinishedEating = datetime.now().strftime("%H:%M:%S")
        peto.currentMeal.petFinishedEating = datetime.now().time().replace(microsecond=0)
        peto.currentMeal.amountEaten = food_eaten
        requests.put(f'{serverURL}:{serverPORT}/push/{peto.id}', data={
            "title": "Finished Eating!",
            "body": f"{peto.petName} ate {food_eaten} grams"
        })
        peto.currentMeal.startedEating = False
        # add to DB
        try:
            x = requests.post(f'{serverURL}:{serverPORT}/meal/pet/{peto.id}',
                              data=json.loads(json.dumps(peto.currentMeal.__dict__, default=str)))
            print(x.text)
        except Error as error:
            print(error.msg)

        # print(f"finished meal sending lunch status amount dog eat :{food_eaten}")
        return schedule.CancelJob


def feed(peto, grams, mealID, mealName):
    peto.currentMeal = Meal(name=mealName, mealTime=datetime.now(), amountGiven=grams)
    # peto.currentMeal.ID = mealID
    # peto.currentMeal.name = mealName
    # peto.currentMeal.mealTime = datetime.now().strftime("%H:%M:%S")
    print("feeding pet")
    num = peto.FeedPet(grams)
    schedule.every(1).minutes.do(check_for_remaining_food, peto)
    x = requests.put(f'{serverURL}:{serverPORT}/push/{peto.id}', data={
        "title": "Meal Is Served!",
        "body": f"{num} grams added to plate"
    })
    print(x)


def feedOnce(peto, grams, mealID, mealName):
    print("feeding pet")
    peto.currentMeal = Meal(name=mealName, mealTime=datetime.now(), amountGiven=grams)
    #
    # peto.currentMeal.ID = mealID
    # peto.currentMeal.name = mealName
    # peto.currentMeal.mealTime = datetime.now().strftime("%H:%M:%S")
    num = peto.FeedPet(grams)
    schedule.every(1).minutes.do(check_for_remaining_food, peto)
    x = requests.put(f'{serverURL}:{serverPORT}/push/{peto.id}', data={
        "title": "Meal Is Served!",
        "body": f"{num} grams added to plate"
    })
    requests.delete(f'{serverURL}:{serverPORT}/meal/{mealID}')
    return schedule.CancelJob


class Scheduler(IScheduler):
    def __init__(self, peto: IPETO, config):
        super().__init__(peto)
        self.peto = peto
        self.config = config
        globals()['serverURL'] = config['DEFAULT']['server_url']
        globals()['serverPORT'] = config['DEFAULT']['server_port']
        globals()['min_scale_val'] = config.getint('SCALE','min_scale_val')
        globals()['max_scale_val'] = config.getint('SCALE','max_scale_val')

    def remove_from_schedule(self, job):
        schedule.cancel_job(job)
        pass

    def add_to_schedule(self, func):
        pass

    def normalRoutine(self):
        self.peto.lightON()
        schedule.every(1).seconds.do(bootupRoutine, self.peto).tag("normalRoutine")
        schedule.every(5).seconds.do(container_status, self.peto).tag("normalRoutine") #should be 10 min
        schedule.every(30).seconds.do(check_for_new_schedule, self.peto).tag("normalRoutine")
        schedule.every(4).seconds.do(should_I_Feed, self.peto).tag("normalRoutine")
        # schedule.every(4).minutes.do(feed, self.peto,30)
        while len(schedule.jobs)!=0:
            schedule.run_pending()
            time.sleep(1)
        # schedule.every().hour.do(job)
        # schedule.every().day.at("10:30").do(job)
        pass
        # we give server our Machine_id and wait for sync with a specific app
    # def bootupRoutine(self):
    #     self.peto.Blink()
    #     while True:
    #         print("finding pair")
    #         time.sleep(3)
    #         try:
    #             result = requests.get(f'{serverURL}:{serverPORT}/pair/{self.peto.machine_id}').json()['pet_id']
    #             print(result)
    #             if result:
    #                 self.peto.id = result
    #                 # lets find pet's name
    #                 self.peto.petName = requests.get(f'{serverURL}:{serverPORT}/pets/{result}').json()['name']
    #                 print("found!")
    #                 self.peto.Blink()
    #                 break
    #
    #         except:
    #             print("failed")
    #
    #     pass

