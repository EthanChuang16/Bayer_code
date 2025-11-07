import os
import random

#paths
base_target_dir = r'Z:\DFCI'
output_file = r'Z:\PythonScripts\ScrambledKey.txt'

#hashmap to map original id to new id
scramble_hashMap = {}
# we dont want dupes
existing_scrambled_ids = set()

try:
  for patient_id in os.listdir(base_target_dir):
    full_path = os.path.join(base_target_dir, patient_id)
    if not os.path.isdir(full_path):
      continue

    #gen random to same lenght for simplcity sake
    length = len(patient_id)
    scrambled_id = None

    #make sure scrambled is unique 
    while True:
      scrambled_id = ''.join([str(random.randint(0,9)) for _ in range(length)])
      #no dupes
      if scrambled_id not in existing_scrambled_ids:
        existing_scrambled_ids.add(scrambled_id)
        break

    #add to our hashmap
    scramble_hashMap[patient_id] = scrambled_id


  #rename the directories now 
  for original_id, scrambled_id in scramble_hashMap.items():
    original_path = os.path.join(base_target_dir, original_id)
    new_path = os.path.join(base_target_dir, scrambled_id)

    try:
      os.rename(original_path, new_path)
      print(f"Renamed: {original_id} -> {scrambled_id}")
    except Exception as rename_err:
      print(f"Failed to rename {original_id}: {rename_err}")

except Exception as e:
  print(f"Error scanning directories: {e}")


#now write the results to a txt file
try:
  with open(output_file, 'w') as f:
    for original, scrambled in scramble_hashMap.items():
      f.write(f"{original} -> {scrambled}\n")
  print(f"Scramble key written to {output_file}")
except Exception as e:
  print(f"Error writing to file: {e}")