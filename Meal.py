class Meal():
        def __init__(self,name=None, mealTime=None, petStartedEating=None, amountGiven=None, amountEaten=None,
                     petFinishedEating=None):
            self.name = name
            self.mealTime = mealTime
            self.petStartedEating = petStartedEating
            self.amountGiven = amountGiven
            self.amountEaten = amountEaten
            self.petFinishedEating = petFinishedEating
            self.startedEating = False
