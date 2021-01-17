import numpy as np
import pandas as pd
from faker import Faker
import random

#Faker.seed(0)
fake = Faker()

class Employee:
  def __init__(self, bool_good_employee, data):
    self.type = bool_good_employee
    self.norm_goals_treshold = data['simulation'][2]
    self.quitting_index = data['simulation'][4]
    self.leave_magn = data['simulation'][7]
    self.goals_setting = data['simulation'][9]

    self.name = fake.first_name()
    print("---------------------")
    print("Employee created:", self.name)
    print("---------------------\n")

    self.contract = {
      'max_vesting': data['contract'][0],
      'vesting_function_type': data['contract'][1],
      'months_of_cliff': round(12*data['contract'][2]),
      'min_months': round(12*data['contract'][3])
    }

    self.states = {
      'abs_month':  np.array([0]),
      'bool_status_working': np.array([1], dtype=bool), #boolean
      'vested_assets': np.array([0]), # can be negative if regressive, and None if totally unvested
      'liquid_assets': np.array([0]),
      'regressive_count': np.array([0]), # how many months of unvesting happened
      'totally_unvested': np.array([1], dtype=bool), # boolean -> does ehe employee have vested money or not
      'weighted_goals': [None], # dictionary of -> goal:weight
      'months_working': np.array([0]),
      'in_cliff': None # will be filled with boolean np array
    }

    self.state = {
      'abs_month': 0,
      'bool_status_working': 1, #boolean
      'vested_assets': 0, 
      'liquid_assets': 0,
      'regressive_count': 0,
      'totally_unvested': 1, # boolean
      # dictionary -> goal:weight
      'weighted_goals': None,
      'months_working': 0,
      'in_cliff': None # boolean
    }

    if self.in_cliff():
      self.states['in_cliff'] = np.array([1], dtype=bool)
      self.state['in_cliff'] = 1
    else:
      self.states['in_cliff'] = np.array([0], dtype=bool)
      self.state['in_cliff'] = 0

  def random_combination(self, iterable, r):
    #"Random selection from itertools.combinations(iterable, r)"
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.sample(range(n), r))
    return tuple(pool[i] for i in indices)

  def add_state(self):
    print("---------------------")
    print("employee function - add_state")
    print("---------------------\n")
    for key in self.state.keys():
      self.states[key] = np.append(self.states[key], self.state[key])

  def set_status_quit(self):
    print("---------------------")
    print("employee function - set_status_quit")
    if self.state['in_cliff']:
      working = 1
    else:
      working = 1 if np.random.random_sample() > self.quitting_index*self.leave_magn else 0
    print("employee function - set_status_quit: Did employee not quit (working)?", working)
    print("---------------------\n")
    return working

  def separate_input(self, pair):
    return tuple(pair.split(':'))

  def receive_input(self):
    print("---------------------")
    print("function employee - receive input\n")
    print(f"Employee name: {self.name}\n")
    print("Insert goals with correspondig weights here\n")
    print("Type goal:weight separated by whitespace\n")
    print("Example: goal_a:3 goal_b:5 goal_c:1\n")

    try:
      raw_input = input("Type here: ")
      goals_weights = {
        goal:int(weight) for goal, weight in map(self.separate_input, raw_input.split())
      }
      
      weighted_goals = {
        goal: {'weight': weight, 'completed': None} for goal, weight in goals_weights.items()
      }

      print("processed input:")
      print("weighted_goals", weighted_goals)
      print("---------------------\n")

      return weighted_goals
    except ValueError:
      print("")
      print("Please insert a valid input")
      print("")
      return self.receive_input()

  def handle_input(self):
    # if entered  here the employee is assume dalready tobe working
    print("---------------------")
    print("function employee - handle input")
    print("---------------------\n")
    goals_setting = self.goals_setting
    if goals_setting == 'Dynamic':
      input = self.receive_input()
      return input
    # if goals_setting = 'Fixed' and is status = True (working)
    # goals for all iteration will be the same
    else:
      try:
        # if not in first iteration (month) just copy the dict of first iteration
        initial_weighted_goals = self.states['weighted_goals'][self.states['weighted_goals'] != np.array(None)][0]
        return initial_weighted_goals
      except:
        print("first iteration, no goals setted yet")
        # if in first iteration (month) we have to receive from user the input of goals and weights
        return self.receive_input()

  def progressive_vesting(self, weighted_goals_input):
    #print("---------------------")
    #print("function employee - progressive_vesting")
    type = self.type
    #print("function employee: is this a good employee?", type)
    norm_goals_treshold = self.norm_goals_treshold
    num_goals = len(list(weighted_goals_input.keys()))
    goals_treshold = norm_goals_treshold*num_goals
    if type: # good employee
      num_goals_completed = np.random.randint(goals_treshold, num_goals)
      # will dictate which goals he has completed
      completed_positions = self.random_combination(range(0,num_goals), num_goals_completed)
    else: # bad employee
      num_goals_completed = np.random.randint(0, goals_treshold)
      completed_positions = self.random_combination(range(0,num_goals), num_goals_completed)
      #np.random.sample(0, num_goals, size=(num_goals_completed))

    print("num_goals_completed", num_goals_completed)
    print("")
    print("num_goals", num_goals)
    print("")
    print("completed_positions", completed_positions)

    # updates goals property ['completed'] according to completed positions
    weighted_sum = 0
    total_sum = 0
    for i, (_, goal_prop) in enumerate(weighted_goals_input.items()):
      total_sum += goal_prop['weight']
      if i in completed_positions:
        goal_prop['completed'] = True
        weighted_sum += goal_prop['weight']
      else:
        goal_prop['completed'] = False

    print("weighted_sum", weighted_sum)
    print("")
    print("total_sum", total_sum)
    print("---------------------\n")

    if self.contract['vesting_function_type'] == 'Linear':
      return (weighted_sum/total_sum)*(self.contract['max_vesting']/self.contract['min_months'])
    else:
      return ((weighted_sum/total_sum)**2)*(self.contract['max_vesting']/self.contract['min_months'])

  def regressive_vesting(self):
    print("---------------------")
    print("function employee - regressive_vesting")
    # if the employee is not working in company regressive vesting is = -progressive
    # if the employee is totally unvested than vesting is None
    regressive_count = self.state['regressive_count']
    if self.state['totally_unvested'] == False:
      print("Can still be unvested")
      self.state['regressive_count'] += 1
      print("---------------------\n")
      old_progressives = self.states['vested_assets'][self.states['vested_assets'] > 0]
      return -old_progressives[regressive_count]
    else:
      print("Totally unvested")
      print("Regressive returns 0")
      print("---------------------\n")
      # returns 0 if the employee already gave back all his assets
      return 0

  def get_vested_assets(self, weighted_goals_input, regressive=False):
    print("---------------------")
    print("function employee - get_vested_assets")
    # update 'weighted_goals':{'completed': } and return vested assets
    if not regressive:
      print("Progressive Vesting")
      print("---------------------\n")
      return self.progressive_vesting(weighted_goals_input)
    else:
      print("Regressive Vesting")
      print("---------------------\n")
      return self.regressive_vesting()
  
  def set_goals_assets(self):
    print("---------------------")
    print("employee - set_goals_assets")
    # working after cliff -> progressive vesting happens
    if self.state['in_cliff'] == False and self.state['bool_status_working'] == True:
      print('########################')
      print("passed cliff and working")
      print('########################')
      print("---------------------\n")
      # weighted_goals_input is a dictionary
      self.state['weighted_goals'] = self.handle_input()
      self.state['vested_assets'] = self.get_vested_assets(self.state['weighted_goals'])
      self.state['liquid_assets'] += self.state['vested_assets']
      if self.state['liquid_assets'] < 1E-15: # so that we dont get  e-19 like numbers
        self.state['liquid_assets'] = 0

    # after cliff, not working, we are setting weights to None
    elif self.state['in_cliff'] == False and self.state['bool_status_working'] == False:
      print('########################')
      print("not in cliff and not working")
      print('########################')
      print("---------------------\n")
      self.state['weighted_goals'] = None
      # he will be unvested -> regressive vesting
      self.state['vested_assets'] = self.get_vested_assets(self.state['weighted_goals'], regressive=True)
      self.state['liquid_assets'] += self.state['vested_assets']
      if self.state['liquid_assets'] < 1E-15:
        self.state['liquid_assets'] = 0

    # working in cliff
    else:
      print('########################')
      print("in cliff and working")
      print('########################')
      print("---------------------\n")
      # when in cliff, we are setting weights (not relevant to algorithm) to None and vesting to 0
      self.state['weighted_goals'] = None
      self.state['vested_assets'] = 0
      self.state['liquid_assets'] += self.state['vested_assets']
      if self.state['liquid_assets'] < 1E-15:
        self.state['liquid_assets'] = 0

    # if employee worked add one month more
    if self.state['bool_status_working'] == True:
      self.state['months_working'] += 1
    print("self.state['months_working']", self.state['months_working'])
    print("-------------------\n")

  def in_cliff(self):
    print("---------------------")
    print("function employee - in_cliff")
    print("---------------------\n")
    print("months of cliff", self.contract['months_of_cliff'])
    if self.state['bool_status_working'] == True:
      if self.state['months_working'] >= self.contract['months_of_cliff']:
        return False
      else:
        return True
    else:
      return False # the employee is not working so he cant be in the cliff

  def set_state(self, month):

    print("@@@@@@@@@@@@@@@@@@@@@")
    print("Setting Next State of Employee:", self.name)
    print("@@@@@@@@@@@@@@@@@@@@@")
    print("")

    print("----------actual state-----------------")
    print("employee.state", self.state)
    print("---------------------------------------\n")

    print("-------history of states --------------")
    print("employee.states", self.states)
    print("---------------------------------------\n")



    # sets goals and assets -> core of the state
    print("")
    print("**entering set_goals_assets**")
    self.set_goals_assets()
    print("**left set_goals_assets**")
    print("")

    # chance of employee quitting
    if self.state['bool_status_working'] and not self.state['in_cliff']:
      self.state['bool_status_working'] = self.set_status_quit() # employee can quit only if he is working
    print("Did the employee quit? (remember if he is fired this will be False aswell):", self.state['bool_status_working'])
    print("---------------------\n")

    # uncliffing employee after cliff
    self.state['in_cliff'] = self.in_cliff()
    print("is employee in cliff now?", self.state['in_cliff'])
    print("---------------------\n")

    # if employee is totally unvested already
    self.state['totally_unvested'] = 1 if self.state['liquid_assets'] == 0 else 0
    print("is employee totally unvested now? (employee has no assets to give)", self.state['totally_unvested'])
    print("---------------------\n")

    #update absolute month -> counting relative to when company started, not relative to the employee
    self.state['abs_month'] = month

    print("months worked by employee:", self.state['months_working'])
    print("---------------------\n")

    print("entering add_state")
    self.add_state()
    print("left_add_state")
    print("---------------------\n")



    
      