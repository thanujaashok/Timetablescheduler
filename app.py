from flask import Flask, render_template
import random
import numpy as np
import copy
from copy import deepcopy
from flask import Flask, render_template, request, redirect, url_for,jsonify,render_template_string
from prettytable import PrettyTable

DAYS = 5
POPULATION = 6
TOTAL_SLOTS = 10
BREAK_SLOTS = [2, 5, 8]
PERIODS = [0, 1, 3, 4, 6, 7, 9]

courses = []
faculties={}

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('admin.html', faculties=faculties)

@app.route('/admin')
def admin():
    return render_template('admin.html')  # You can adjust the template name as needed


@app.route('/edit')
def edit():
    return render_template('edit.html')

@app.route('/facultyedit')
def facultyedit():
    return render_template('facultyedit.html')




@app.route('/update_course', methods=['POST'])
def update_course():
    global courses
    # Get form data
    course_name = request.form.get('course-name')
    course_type = request.form.get('course-type')
    faculty = request.form.get('faculty')
    credits = request.form.get('credit')

    # Create a dictionary for the course
    course_data = {
        'name': course_name,
        'faculty':faculty,
        'type': course_type,
        'credits': int(credits)
    }

    # Append the course to the courses list
    courses.append(course_data)

    # Redirect back to the edit page
    return redirect(url_for('edit'))

@app.route('/update_faculty', methods=['POST'])
def update_faculty():
    global faculties
    # Get form data
    
    faculty_name = request.form.get('faculty-name')
    course_name = request.form.get('course-name')
    credits_theory = request.form.get('credits-theory')
    credits_practical = request.form.get('credits-practical')

    # Create a dictionary for the course
    course_data = {
        'name': course_name,
        'max_credits_theory': int(credits_theory),
        'max_credits_practicals':int(credits_practical)
    }

    # Append the course to the courses list
    faculties[faculty_name]=course_data

    # Redirect back to the edit page
    return redirect(url_for('facultyedit'))

from flask import render_template

@app.route('/timetable')
def timetable_page():
    try:
        timetable_data = generate_timetables()
        if timetable_data:
            return render_template('timetable.html', timetable_data=timetable_data)
        else:
            return "Error generating timetable data."
    except Exception as e:
        return f"An error occurred: {str(e)}"

    


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


def generate_timetables():
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
                print(f"Iteration {i}, Loss: {loss}")

            new_schedules = [[["BREAK" if x in BREAK_SLOTS else 0 for x in range(TOTAL_SLOTS)] for z in range(POPULATION)]]
            schedules[0] = copy.deepcopy(best)
            schedules[1] = copy.deepcopy(best2)

            for j in range(2, POPULATION):
                schedules[j] = _mutate(_combine(copy.deepcopy(schedules[0]), copy.deepcopy(schedules[1])))

    except Exception as e:
        return schedules[0]

    # Returning the best schedule after optimization
    return schedules[0]

    




if __name__ == '__main__':
    app.run(debug=True)
    