# delete files and folders from before

import os

path = "./output" # path from where its called -> called always from main

employees_folder = "\\employees\\"

for root, dirs, files in os.walk(path):
  for file in files:
    if file.endswith((".csv", ".png")): # The arg can be a tuple of suffixes to look for
      path_to_file = os.path.join(root, file)
      print("removing:", path_to_file)
      os.remove(path_to_file)

for root, dirs, files in os.walk(path):
  for dir in dirs:
    path_to_folder = os.path.join(root, dir)
    if employees_folder in path_to_folder:
      print("removing:", path_to_folder)
      os.rmdir(path_to_folder)