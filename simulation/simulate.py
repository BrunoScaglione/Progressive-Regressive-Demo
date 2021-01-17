# - runs simulation 
# #-> saves csv files containing history of states and returns history of employees

import glob
import os
import sys

def simulate(path_to_input, path_to_output, from_main=True):
  if from_main:
    from simulation.modules.employee import Employee
    from simulation.modules.company import Company
    from simulation.options.init import init_options
  else:
    from modules.employee import Employee
    from modules.company import Company
    from options.init import init_options

  contract_opt, simulation_opt, _ = init_options(path_to_input)
  company = Company(contract_opt, simulation_opt, path_to_output, from_main=from_main)
  company.run()

if __name__ == "__main__":

  path_to_input = '../input'
  path_to_output = '../output'
  simulate(path_to_input, path_to_output, from_main=False)
