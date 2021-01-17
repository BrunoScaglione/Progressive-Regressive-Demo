# executes Progresive Regressive Algorithm
# based on Demo Options

# Author: Bruno Scaglione
# Linkedin: https://www.linkedin.com/in/bruno-scaglione-4412a0165/

import subprocess
import os
import sys

from simulation.simulate import simulate

path_to_input = './input'
path_to_output = './output'

# clean output
subprocess.run("python utils/clean.py")
simulate(path_to_input, path_to_output)
# build plots and save to output/figures
subprocess.run("python plots.py")

