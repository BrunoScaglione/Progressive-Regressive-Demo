import numpy as np
import pandas as pd
import copy
import os
import sys

# because its the path relative to simulate.py script which is  the process running

class Company:

  def __init__(self, contract_opt, simulation_opt, path_to_output, from_main=True):

    self.from_main = from_main

    self.path_to_output = path_to_output

    self.data = {
      'contract': contract_opt.iloc[0].values,
      'simulation': simulation_opt.iloc[0].values
    }

    self.employees = {
      'num_working_employees': np.array([self.data['simulation'][1]]), 
      'num_entering_employees': np.array([self.data['simulation'][1]]),
      'num_leaving_employees': np.array([0]),
      'num_fired_employees': np.array([0]),
      'num_quitted_employees': np.array([0]),
       # note: this property will have on element less, None will be added in the end of the loop, at the first position to match
      'employees': [], # will be filled with self.get_employees_types() and contains all employees (even if not working)
      'bad_employee_index': self.data['simulation'][8]
    }
    
    self.model = {
      'months_of_simulation': round(12*self.data['simulation'][0]),
      'hire_index': self.data['simulation'][3],
      'fire_index': self.data['simulation'][5],
      'hire_magn': self.data['simulation'][6],
      'leave_magn': self.data['simulation'][7],
      'growth_function_type': self.data['simulation'][10],
      'initial_value': (10**6)*self.data['simulation'][11], # last value = initial value in the beggining
      'growth_magn': self.data['simulation'][12]
    }

    self.states = {
      'remaining_assets': np.array([100]), # in %
      'progressive_assets': np.array([0]), # per month
      'regressive_assets': np.array([0]), # per month
      'liquid_assets': np.array([0]), # per month
      'market_value': np.array([self.model['initial_value']])
    }

    self.set_new_employees(init=True)

  def bring_Employee(self, bool_good_employee, data):
    print("function bring_Employee")
    if self.from_main:
      from simulation.modules.employee import Employee
    else: # executing from simulate.py
      from modules.employee import Employee
    return Employee(bool_good_employee, data)

  def set_market_value(self):
    print("function set_market_value")
    if self.model['growth_function_type'] == 'Linear':
      # growth magnitude here describes how much per month the company gains value (independent of value of the company)
      # hypothsis of maximum growth per month of 1 billion dollars
      self.states['market_value'] = np.append(self.states['market_value'], self.model['market_value'][-1] + np.interp(self.model['growth_magn'], [0,1], [0, 10**9]))
    else:
      # exponential, growth magnitude is normalized by value of the company (% of growth) 
      print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
      print("exponential market value:", self.states['market_value'][-1] + self.model['growth_magn']*self.states['market_value'][-1])
      self.states['market_value'] = np.append(self.states['market_value'], self.states['market_value'][-1] + self.model['growth_magn']*self.states['market_value'][-1])

  def set_entering_employees(self):
    # binomial distribution
    print("function set_entering_employees")
    p = self.model['hire_index']
    n = self.model['hire_magn']*self.employees['num_working_employees'][-1]
    entering = np.random.binomial(n, p)
    self.employees['num_entering_employees'] = np.append(self.employees['num_entering_employees'], entering)
    # update num_working_employees, do not append because its not a new iteration, we are just combining
    # the effect of leaving(already appended) with entering
    self.employees['num_working_employees'][-1] = self.employees['num_working_employees'][-1] + entering
  
  def get_employees_types(self): # , init=False
    print("function get_employee_types")
    num_bad_employees = round(self.employees['bad_employee_index']*self.employees['num_entering_employees'][-1])
    num_good_employees = self.employees['num_entering_employees'][-1] - num_bad_employees
    employees_types = [0 for i in range(int(num_bad_employees))] + [1 for j in range(int(num_good_employees))]
    print("function get_employee_types : eployees_types:", employees_types)
    return employees_types

  def set_status_fire(self, employee):
    print("function set_status_fire")
    if employee.state['in_cliff']:
      print("employee in cliff - wont be fired")
      working = 1
    else:
      working = 1 if np.random.random_sample() > self.model['fire_index']*self.model['leave_magn'] else 0
      print("Did employee not get fired?(working)", working)
    return working

  def set_employees(self, month):
    print("function set_employess")
    num_employees = 0
    num_quitted = 0
    num_fired = 0
    for employee in self.employees['employees']:
      # update employees states
      employee.set_state(month)

      # employees that quitted in this month
      if employee.states['bool_status_working'][-1] != employee.states['bool_status_working'][-2]:
        num_quitted += 1

      # update self.employees based on employees entering and leaving
      if employee.state['bool_status_working']:
        # if employees have not quitted, might still get fired
        if not self.set_status_fire(employee):
          employee.state['bool_status_working'] = 0
          # because the state was already added inside the emplloyee so we have to change the history also
          employee.states['bool_status_working'][-1] = 0
          num_fired += 1
        else:
          num_employees += 1
          
    # store new num working employees based on employees that might have quitted or fired
    self.employees['num_working_employees'] = np.append(self.employees['num_working_employees'], num_employees)

    self.employees['num_fired_employees'] = np.append(self.employees['num_fired_employees'], num_fired)

    self.employees['num_quitted_employees'] = np.append(self.employees['num_quitted_employees'], num_quitted)

    self.employees['num_leaving_employees'] = np.append(self.employees['num_leaving_employees'], num_fired+num_quitted) 

  def set_new_employees(self, init=False):
    # also runs in the begginig, assume initial employees are "entering"
    print("function set_new_employees")
    if not init: # not the the beggining
      self.set_entering_employees() # gets num of entering employeesnd updates entering and working employees
    entering_employees_types = self.get_employees_types() # gets types (good/bad) array
    #entering_employees = [Employee(bool_good_employee, self.data) for bool_good_employee in entering_employees_types]
    entering_employees = [self.bring_Employee(bool_good_employee, self.data) for bool_good_employee in entering_employees_types]
    # update array of employees (instances)
    self.employees['employees'] = self.employees['employees'] + entering_employees # concatenate

  def build_tensors_and_employeetocsv(self):
    # to build matrix of assets (employees arrays verticaly stacked ) we need to match number of states of employees
    # get len of vesting of oldest employee and fill all other employees with zeros to match it
    print("function build_tensors_and_employeetocsv")
    max_time = len(self.employees['employees'][0].states['vested_assets'])

    matrix_assets = None
    list_employees_states = [] #  will hold history of states of all employees
    for employee in self.employees['employees']:
      padding = np.full(max_time - len(employee.states['vested_assets']), 0)

      if employee.state['months_working'] > 0: # employees that entered in last month dont count
        if matrix_assets is not None:
          # vertical stacking of arrays -> matrix
          vesting_with_padding = np.append(employee.states['vested_assets'].copy(), padding)
          matrix_assets = np.append(matrix_assets, [vesting_with_padding], axis=0)
        else:
          matrix_assets = np.array([employee.states['vested_assets']]) # first iteration

        list_employees_states.append(employee.states.copy())
        matrix_states = np.array(list(employee.states.values())) # employee.states.values() returns a view in python 3
        array_names_states = np.array(list(employee.states.keys()))
        # save to csv files employees states history
        transposed_matrix = np.transpose(matrix_states)
        employee_df = pd.DataFrame(transposed_matrix, columns=array_names_states)
        employee_df.to_csv(self.path_to_output+"/csv files/employees/employee_"+employee.name+".csv")

    return (matrix_assets, list_employees_states)

  def set_company_state_and_companytocsv(self, matrix_assets):
    print("function set_company_state_and_companytocsv")
    # progressive values
    progressive_matrix_assets = copy.deepcopy(matrix_assets)
    progressive_matrix_assets[progressive_matrix_assets < 0] = 0
    self.states['progressive_assets'] = np.sum(progressive_matrix_assets, axis=0)
    # regressive values
    regressive_matrix_assets = copy.deepcopy(matrix_assets)
    regressive_matrix_assets[regressive_matrix_assets > 0] = 0
    self.states['regressive_assets'] = np.sum(regressive_matrix_assets, axis=0)
    # liquid assets
    self.states['liquid_assets'] = self.states['progressive_assets'] + self.states['regressive_assets']
    # remaining assets in % of company's assets
    self.states['remaining_assets'] = [100 - np.sum(self.states['liquid_assets'][:i+1]) for i in range(len(self.states['liquid_assets']))]

    # save to cvs files states history of company
    print("function set_company_state_and_companytocsv: transposed matrix:", np.transpose(np.array(list(self.states.values()))))
    print("function set_company_state_and_companytocsv: columns:", list(self.states.keys()))
    company_df = pd.DataFrame(np.transpose(np.array(list(self.states.values()))), columns=list(self.states.keys()))
    company_df.to_csv(self.path_to_output+"/csv files/company/company.csv")

  def company_employees_to_csv(self):
    print("----------------------")
    print("function company_employees_to_csv")
    print("----------------------\n")
    # interesting to save history of num working employees and num entering employees
    company_employees_df = (
      pd.DataFrame(np.transpose(np.array(list(self.employees.values())[:5])), columns=np.array(list(self.employees.keys())[:5]))
    )

    company_employees_df.to_csv(self.path_to_output+"/csv files/company/employees.csv")



  def run(self):
    print("---------------------")
    print('Company.data:', self.data)
    print("---------------------\n")

    print("---------------------")
    print('Company.model:', self.model)
    print("---------------------\n")

    for month in range(1, self.model['months_of_simulation']+1): 
      # initial state already stored
      print("$$$$$$$$$$$$$$$$$$$$$$")
      print("$$$$$$$$$$$$$$$$$$$$$$")
      print("month:", month)
      print("$$$$$$$$$$$$$$$$$$$$$$")
      print("$$$$$$$$$$$$$$$$$$$$$$\n")

      print("---------------------")
      print('Company.states:', self.states)
      print("---------------------\n")


      print("---------------------")
      print('Company.employees:', self.employees)
      print("---------------------\n")

      # update employees vesting, working state(fire or quit), number of working employees
      # month+1 because 
      self.set_employees(month)
      
      # append new employees 
      # create Employees based on get_employees_types
      self.set_new_employees()
      
      # update value of company
      self.set_market_value()

    # building assets states of company (based on history of all employees)
    # and saving all history to csv files
    matrix_assets, list_employees_states = self.build_tensors_and_employeetocsv()
    self.set_company_state_and_companytocsv(matrix_assets)
    # first two prop of self.employees to csv
    self.company_employees_to_csv()

    print("---------------------")
    print("rows are employees, columns are month and elements represent amount vested (can be negative)")
    print("matrix assets:", matrix_assets)
    print("---------------------\n")

    print("---------------------")
    print("list containing history of states for each employee")
    print("list_employees_states", list_employees_states)
    print("---------------------\n")

