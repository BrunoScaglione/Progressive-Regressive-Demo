# reads the excel options file and returns 2 dictionaries
# of options chosen by the user.
# options_run: options to run the simulation.
# options_show: options toshow results.

from tabulate import tabulate
import pandas as pd 
import os
import sys

def init_options(path_to_input):

  # dict with all sheets as dataframes
  df_dict = pd.read_excel(
    path_to_input+'/Demo options.xlsx',
    sheet_name = ['Contract options', 'Simulation options','Results options'],
    nrows=1
  )
  contract_opt = df_dict['Contract options']
  simulation_opt = df_dict['Simulation options']
  show_opt = df_dict['Results options']
  #print((contract_opt, simulation_opt, show_opt)) # there are a lot of extra NaN rows, little weird, but wont influence
  return (contract_opt, simulation_opt, show_opt)

if __name__ == "__main__":
  # print dataframes
  contract_opt, simulation_opt, show_opt = init_options('../../input')
  print("\n\n")
  print("######### Transposed Dataframes #########")
  # there are a lot of extra NaN columns, little weird, but wont influence
  print("\n\n")
  print("Contract options:")
  print(tabulate(contract_opt.transpose(), headers = 'keys', tablefmt = 'psql'))
  print("\n\n")
  print("Simulation options:")
  print(tabulate(simulation_opt.transpose(), headers = 'keys', tablefmt = 'psql'))
  print("\n\n")
  print("Results options:")
  print(tabulate(show_opt.transpose(), headers = 'keys', tablefmt = 'psql')) 