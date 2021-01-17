# ProRe Demo - Progressive Regressive Vesting Algorithm Simulation

## Description

ProRe Demo is a simulation of a new method of asset transfer between companies
and employees: the Progressive Regressive asset transfer.

The Progressive Regressive algorithm consists of two parts: progressive and regressive stages.

1. Progressive: in progressive vesting, employees get vested according to a function of the ratio of goals completed by all goals, in the month.

2. Regressive: in regressive vesting, when employees aren't working for the company anymore they get "unvested", which means they transfer back received assets. This transfer occurs exactly how the progressive vesting ocurred.

This method is intended to avoid asset erosion, retain talents and provide extra incentive for them.

## Requirements

The project has some dependecies that need to be installed first.

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies.

```bash
pip install numpy pandas tabulate matplotlib seaborn faker
```

## Structure (folders and files)

The root directory:
  - main.py &#8594; runs the simulation based on input options and saves results as csv files and png images;
  - plots.py &#8594; uses csv files to create plots and save as png images based on input options;
  - simulation &#8594; contains files regarding the algorithm;
      - options;
          - init.py &#8594; loads options from excel.
      - modules &#8594; contains files of entities of the simulation.
          - company.py &#8594; class Company;
          - employee.py &#8594; class Employee.
      - simulate.py &#8594; runs the simulation based on input options;
  - utils &#8594; contains complementary files
      - clean.py &#8594; deletes all files and folders generated in output;
      - dummy_goals.txt &#8594; example of in-simulation input of goals with weights that can be copy pasted.
  - input &#8594; contains input file, which is an excel with multiple sheets;
      - Demo options.xlsx &#8594; excel file with parameters to be edited.
  - output &#8594; contains output files generated by simulate.py and plots.py.
      - csv files &#8594; contains resulting csv files;
          - company &#8594; contains company's states history and employee's (as a group) states history;
          - employees &#8594; contains individual employee's states history for each employee.
      - figures  &#8594; contains resulting plots.
          - company &#8594; contains plots of the company's states history combined with employee's (as a group) states history;
          - employees &#8594; contains plots of employee's states history for each employee.

## Usage

### Input 

The file Demo options has 4 sheets: 
  - Index &#8594; explanation of paramaters, details of model and notes;
  - Contract options &#8594; contract parameters;
  - Simulations options &#8594; simulation parameters;
  - Results options &#8594; results parameters.
    
### Output

 ```bash 
    output/csv
  ``` 
Above folder stores the states history (csv files) of employees and the company, generated on the simulation by simulate.py.

 ```bash 
   output/figures
   ``` 
Above folder stores plots (png images) of attributes of the employee's and company's states history. Details can be seen in "Results options" sheet of the "Demo options" file.

### Commands

* to run the simulation, save csv and png files and plot results:

```bash
   python main.py
```

* only to run the simulation and save csv files:

```bash
   cd simulation
   python simulate.py
```

* only to plot results:

```bash
   python plots.py
```

* only to delete or clean results:

```bash
   cd utils
   python clean.py
```

## Simulation

In the simulation you will be requested to input, in the terminal, the goals with corresponding weights for each employee for each month he is working (except if you have selected "goals_setting" as "fixed", in this case only for the first month of each employee).

The format must be each goal:weight separated by whitespace.

An example: goal_a:3 goal_b:5 goal_c:1.

```bash
   utils/dummy_goals.txt
```
Above file has an example with more goals.

## Authors

Renato Baccaro is the patent owner. Here is his [linkedin](https://www.linkedin.com/in/baccaro/) profile

Bruno Scaglione is the author of the project. Here is my [linkedin](https://www.linkedin.com/in/bruno-scaglione-4412a0165/) profile. 
