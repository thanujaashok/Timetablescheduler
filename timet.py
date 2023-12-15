import random
import numpy as np
import copy
from copy import deepcopy

DAYS = 5

POPULATION = 6
TOTAL_SLOTS=10
BREAK_SLOTS=[2,5,8]
PERIODS = [0,1,3,4,6,7,9]


faculties = {

        "Karthika": {"name": "DAA", "max_credits_theory": 3, "max_credits_practicals": 1.5},

        "Mohanavalli": {"name": "DAA", "max_credits_theory": 3, "max_credits_practicals": 1.5},

        "Paul": {"name": "OS", "max_credits_theory": 3, "max_credits_practicals": 1.5},

        "Thanik": {"name": "OS", "max_credits_theory": 3, "max_credits_practicals": 1.5},

        "Valli": {"name": "SOftware engn", "max_credits_theory": 3, "max_credits_practicals": 1.5},

        "Kolandhai": {"name": "SOftware engn", "max_credits_theory": 3, "max_credits_practicals": 1.5},

        "Srini": {"name": "Information theory", "max_credits_theory": 3, "max_credits_practicals": 1.5},

        "Theerthana": {"name": "POM", "max_credits_theory": 3, "max_credits_practicals": 1.5},

        "Saravanan": {"name": "AI", "max_credits_theory": 3, "max_credits_practicals": 1.5}

    }
courses = [

        {"name": "SOftware engn lab", "faculty": "Valli", "type": "Practicals", "credits": 2},

        {"name": "OS lab", "faculty": "Paul", "type": "Practicals", "credits": 2},

        {"name": "DAA lab", "faculty": "Mohanavalli", "type": "Practicals", "credits": 2},

        {"name": "SOftware engn", "faculty": "Valli", "type": "Theory", "credits": 3},

        {"name": "OS", "faculty": "Paul", "type": "Theory", "credits": 3},

        {"name": "DAA", "faculty": "Mohanavalli", "type": "Theory", "credits": 3},

        {"name": "Information theory", "faculty": "Srini", "type": "Theory", "credits": 3},

        {"name": "POM", "faculty": "Theerthana", "type": "Theory", "credits": 3},

        {"name": "AI", "faculty": "Saravanan", "type": "Theory", "credits": 3},

    ]

def _loss(schedule):
  loss = 0
  for i in range(DAYS):
    if schedule[i][0] == 0:
      loss += 10
  for i in range(DAYS):
    for j in PERIODS:
      if schedule[i][j]==0:
        if j+1<TOTAL_SLOTS:
          if schedule[i][j + 1] == 0:
              loss += 10
          elif j+2<TOTAL_SLOTS and schedule[i][j+1] == "BREAK" and schedule[i][j + 2] == 0:
              loss+=10

  for i in range(DAYS):
    for j in PERIODS:
      for k in PERIODS:
        if j != k:
          if schedule[i][j]!= 0 and schedule[i][j] == schedule[i][k] and schedule[i][j]['type']=="Theory":
            loss += 5
  for i in range(DAYS):
      for j in PERIODS:
          if schedule[i][j] != 0 and schedule[i][j]['type'] == 'Practicals':
              current_stretch = 0
              course = schedule[i][j]['name']
              c = schedule[i][j]['credits']
              for k in PERIODS:
                  # Check if the element is a dictionary before accessing its 'name' key
                  if isinstance(schedule[i][k], dict) and schedule[i][k]['name'] == course:
                      current_stretch += 1
              if current_stretch == c:
                  break
              else:
                  loss += 100


  for course in courses:
    course_credits = 0
    for i in range(DAYS):
      for j in PERIODS:
        if schedule[i][j] == course:
          course_credits += 1
    loss += 10*(np.abs(course_credits - course['credits']))
  return loss
# for schedule in schedules:
#   print(_loss(schedule))

def _mutate(schedule):

    mutated_schedule = deepcopy(schedule)
    # Mutate: If the first period in a day is free, swap with any non-practical period in the same day
    for day in range(DAYS):
        if schedule[day][0] == 0:  # Check if the first period is free
            non_practical_periods = [p for p in PERIODS if schedule[day][p] != 0 and schedule[day][p]['type'] != 'Practicals']
            if non_practical_periods:
                # Swap the first period with a non-practical period
                period_to_swap = random.choice(non_practical_periods)
                mutated_schedule[day][0], mutated_schedule[day][period_to_swap] = (mutated_schedule[day][period_to_swap],mutated_schedule[day][0])
    for day in range(DAYS):
        for period in PERIODS:
            if (
                schedule[day][period] != 0
                and schedule[day][period] == schedule[day][period + 1] and schedule[day][period]['type']=="Theory"
            ):
                # Find a random period to swap with
                period_to_swap = random.choice([p for p in PERIODS if p != period and schedule[day][p] == 0 and schedule[day][p]['type'] != 'Practicals'])
                mutated_schedule[day][period], mutated_schedule[day][period_to_swap] = (
                    mutated_schedule[day][period_to_swap],
                    mutated_schedule[day][period],
                )

    return mutated_schedule


def _combine(sch1, sch2):
  schedule =[[["BREAK" if x in BREAK_SLOTS else 0 for x in range(TOTAL_SLOTS)] for y in range(DAYS)] for z in range(POPULATION)]
  if random.randint(1,2)==1:
    schedule[:2] = sch1[0:2]
  else:
    schedule[:2] = sch2[0:2]
  if random.randint(1, 2) == 1:
    schedule[6:8] = sch1[6:8]
  else:
    schedule[6:8] = sch2[6:8]
  return schedule

def visualize_timetable(schedule):
    days_week = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]

    for i in range(DAYS):
        print("Day: ", days_week[i])
        for j in range(TOTAL_SLOTS):
            if j in PERIODS:
                if schedule[i][j] == 0:
                    print("PERIOD: ", j, " FREE")
                elif schedule[i][j] == "BREAK":
                    print("BREAK")
                else:
                    course = schedule[i][j]['name']
                    faculty = faculties[schedule[i][j]['faculty']]['name']
                    course_type = schedule[i][j]['type']
                    print("PERIOD: ", j, f"{course} ({course_type}) with {faculty}")
            else:
                print("BREAK")
        print("\n")

def visualize_faculty_timetable(faculty_name, schedule):
    print(f"Timetable for {faculty_name}:")
    days_week = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]

    for i in range(DAYS):
        print(f"\nDay: {days_week[i]}")
        for j in range(TOTAL_SLOTS):
            if j in PERIODS:
                if schedule[i][j] == 0:
                    print(f"PERIOD: {j} FREE")
                elif schedule[i][j] == "BREAK":
                    print("BREAK")
                elif schedule[i][j]['faculty'] == faculty_name:
                    course = schedule[i][j]['name']
                    course_type = schedule[i][j]['type']
                    print(f"PERIOD: {j} {course} ({course_type})")
            else:
                print("BREAK")


schedules = [[["BREAK" if x in BREAK_SLOTS else 0 for x in range(TOTAL_SLOTS)] for y in range(DAYS)] for z in range(POPULATION)]
for schedule in schedules:
    # Allocate practical sessions
    for course in courses:
        if course['type'] == 'Practicals':
            consecutive_hours = course["credits"]  # Number of consecutive hours for the practical session
            allocated = False

            while not allocated:
                day = random.randint(0, DAYS - 1)
                period = random.choice(PERIODS)

                # Check if consecutive slots are available, skipping break slots
                consecutive_slots = []
                for i in range(consecutive_hours):
                    current_period = period + i
                    if current_period < len(PERIODS) and current_period not in BREAK_SLOTS and schedule[day][current_period] == 0:
                        consecutive_slots.append(current_period)

                if len(consecutive_slots) == consecutive_hours:
                    # Allocate practical session in consecutive hours, skipping break slots
                    for i in range(consecutive_hours):
                        schedule[day][consecutive_slots[i]] = course
                    allocated = True

    for course in courses:
      if course['type'] == 'Theory':
        for i in range(course["credits"]):
          day = random.randint(0, DAYS - 1)
          period = random.choice(PERIODS)
          #print(day,period)
          while(schedule[day][period] != 0):
            day = random.randint(0, DAYS - 1)
            period = random.choice(PERIODS)
          schedule[day][period] = course


try:
  loss = 0
  best = None
  for i in range(20000):
    loss1 = _loss(schedules[0])
    loss2 = _loss(schedules[1])
    if loss1 < loss2:
      best = schedules[0]
      best_loss = loss1
      best2 = schedules[1]
      best2_loss = loss2
    else:
      best = schedules[1]
      best_loss = loss2
      best2 = schedules[0]
      best2_loss = loss1
    for j in range(2, POPULATION):
      loss = _loss(schedules[j])
      if loss < best_loss:
        best2 = best
        best2_loss = best_loss
        best = schedules[j]
        best_loss = loss
      elif loss <= best2_loss:
        best2 = schedules[j]
        best2_loss = loss
    loss = best_loss
    if loss == 0:
      break
    if i % 1000 == 0:
      loss
    new_schedules = [[["BREAK" if x in BREAK_SLOTS else 0 for x in range(TOTAL_SLOTS)] for z in range(POPULATION)]]
    schedules[0] = copy.deepcopy(best)
    schedules[1] = copy.deepcopy(best2)
    for j in range(2, POPULATION):
      schedules[j] = _mutate(_combine(copy.deepcopy(schedules[0]), copy.deepcopy(schedules[1])))
except:
   visualize_timetable(schedules[0])
   print(schedules[0])
   #visualize_faculty_timetable("Mohanavalli", schedules[0])


