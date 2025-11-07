import os
import shutil

root_dir = "Z:/DFCI_Anon" 

all_patients = set()
root_patients = []
group_patients = []

#collect patients in root
for d in os.listdir(root_dir):
    path = os.path.join(root_dir, d)
    if os.path.isdir(path) and d != "DFCI_Figs" and not d.startswith("group_"):
        root_patients.append(d)
        all_patients.add(d)

#collect patients in group folders
for g in range(1, 101): 
    group_dir = os.path.join(root_dir, f"group_{g:02d}")
    if os.path.exists(group_dir):
        for d in os.listdir(group_dir):
            path = os.path.join(group_dir, d)
            if os.path.isdir(path):
                group_patients.append(d)
                all_patients.add(d)

#print
print("Patients in root:", len(root_patients))
print("Patients in groups:", len(group_patients))
print("Total unique patients:", len(all_patients))

#check duplicates (patients in root and also inside groups)
dupes = set(root_patients).intersection(set(group_patients))
if dupes:
    print("⚠️ Duplicates found in root and groups:", dupes)
else:
    print("No duplicates.")


