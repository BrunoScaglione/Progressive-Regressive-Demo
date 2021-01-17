# plots results (history dataframes) based on options_show
# exports results (history dataframes) to excel

import numpy as np
import pandas as pd
import os
from tabulate import tabulate
import matplotlib.pyplot as plt
import seaborn as sns

sns.set()

from simulation.options.init import init_options

_, _, show_opt = init_options('./input')

try:
  df_company = pd.read_csv('./output/csv files/company/company.csv')
  df_company_employees = pd.read_csv('./output/csv files/company/employees.csv')

  dfs_employees = {}

  for root, dirs, files in os.walk('./output/csv files/employees'):
    for file in files:
      if file.endswith((".csv")): # The arg can be a tuple of suffixes to look for
        employee_name = file[:-4].replace("employee_", "")
        dfs_employees[employee_name] = pd.read_csv(os.path.join(root, file))

  num_employees = len(list(dfs_employees.values()))

except:
  print("")
  print("There are no files, please run main.py or simulate.py")
  print("")
  raise

print("Show options")
print(tabulate(show_opt.transpose(), headers = 'keys', tablefmt = 'psql'))
print("\n\n")
print("Company states hist")
print(tabulate(df_company.transpose(), headers = 'keys', tablefmt = 'psql'))
print("\n\n")
print("Company employees hist")
print(tabulate(df_company_employees.transpose(), headers = 'keys', tablefmt = 'psql'))
print("\n\n")
print("Employee states (of one random employee) hist")
print(tabulate(list(dfs_employees.values())[0].transpose(), headers = 'keys', tablefmt = 'psql'))

path_to_figures_company = "./output/figures/company"
path_to_figures_employees = "./output/figures/employees"

def plot(data, column, employee=True):
  print("Plotting")
  plot_name = column
  if employee:
    # data is a dictionary of dataframes in this case
    for name_employee, df_employee in data.items():
      ax = sns.lineplot(data=df_employee, x="abs_month", y=column)
      sns.scatterplot(data=df_employee, x="abs_month", y=column)  
      ax.set_title(f"{name_employee} - {plot_name}")   
      #plt.show() # if uncommented you will have to close the figure to see the next one
      employee_path = path_to_figures_employees+f"/{name_employee}"
      if not os.path.isdir(employee_path):
        os.mkdir(employee_path) 
      plt.savefig(employee_path+"/"+plot_name+".png")
      #plt.show() # to show interactively
      plt.close()
  else:
    # data is list of dataframes in this case
    #plots something
    company_df = data[0]
    company_employees_df = data[1]

    _, ax = plt.subplots(2, 1, sharex=True)
    sns.lineplot(data=company_df, x=company_df.index, y=column, ax=ax[0])
    sns.scatterplot(data=company_df, x=company_df.index, y=column, ax=ax[0])
    # plot num working employees
    sns.lineplot(data=company_employees_df, x=company_df.index, y="num_working_employees", ax=ax[1])
    sns.scatterplot(data=company_employees_df, x=company_df.index, y="num_working_employees", ax=ax[1])

    ax[0].set_title(f"Company - {plot_name}")
    ax[1].set_title(f"Company - number of working employees")

    plt.savefig(path_to_figures_company+"/"+plot_name+".png")
    #plt.show() # to show interactively
    plt.close()

if show_opt.at[0,"employee's vesting history with status"]:
  plot(dfs_employees, "vested_assets")
    
if show_opt.at[0,"employee's liquid assets history"]:
  plot(dfs_employees, "liquid_assets")

if show_opt.at[0,"employee's in cliff status history"]:
  plot(dfs_employees, "in_cliff")

if show_opt.at[0,"employee's months working history"]:
  plot(dfs_employees, "months_working")

if show_opt.at[0,"employee's working status history"]:
  plot(dfs_employees, "bool_status_working")

  ################################################

data = [df_company, df_company_employees]

if show_opt.at[0,"company's remaining assets history"]:
  plot(data, "remaining_assets", employee=False)

if show_opt.at[0,"company's regressive assets history, with num working employees"]:
  plot(data, "progressive_assets", employee=False)

if show_opt.at[0,"company's progressive assets history, with num working employees"]:
  plot(data, "regressive_assets", employee=False)

if show_opt.at[0,"company's liquid assets variation history, with num working employees"]:
  plot(data, "liquid_assets", employee=False)

if show_opt.at[0,"company's market value history, with num working employees"]:
  plot(data, "market_value", employee=False)
