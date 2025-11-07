import os
import shutil
from math import ceil

#paths 
root_dir = "Z:/DFCI_Anon"
num_groups = 20

#patient dir excluding dfci_figs and csv file

patient_dirs = [
    d for d in os.listdir(root_dir)
    if os.path.isdir(os.path.join(root_dir, d))
    and d != "DFCI_Figs"
    and not d.startswith("group_")
]


total_patients = len(patient_dirs)
group_size = ceil(total_patients / num_groups)

print(f"Found {total_patients} patient dirs, {group_size} per group.")

#create and move directorise into gorups
for i in range(num_groups):
  group_dir = os.path.join(root_dir, f"group_{i+1:02d}")
  print(f"[Group {i+1}] Would create {group_dir}")
  os.makedirs(group_dir, exist_ok=True)
  print(f"[Group {i+1}] Created {group_dir}")

  #next chunk 
  chunk = patient_dirs[i*group_size:(i+1)*group_size]

  for patient in chunk:
    src = os.path.join(root_dir, patient)
    dst = os.path.join(group_dir, patient)
    print(f"  Moving {patient} -> {group_dir}")
    shutil.move(src, dst)


print(f"Moved {total_patients} patient dirs into {num_groups} groups.")