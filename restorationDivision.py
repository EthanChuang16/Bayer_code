import os
import shutil

#paths
root_dir = "Z:/DFCI_Anon"
num_groups = 100
dry_run = True  #set to False to actually move files

#loop through each group folder
for i in range(num_groups):
    group_dir = os.path.join(root_dir, f"group_{i+1:02d}")
    if not os.path.isdir(group_dir):
        print(f"[Group {i+1}] Skipping (does not exist)")
        continue

    #get patient dirs inside the group folder
    patient_dirs = [
        d for d in os.listdir(group_dir)
        if os.path.isdir(os.path.join(group_dir, d))
    ]

    print(f"[Group {i+1}] Found {len(patient_dirs)} patients to move back")

    for patient in patient_dirs:
        src = os.path.join(group_dir, patient)
        dst = os.path.join(root_dir, patient)

        if os.path.exists(dst):
            print(f"  [WARN] {patient} already exists in root_dir. Possible duplicate!")
            #optional: compare contents before deciding
            continue


        print(f"  Would move {patient} -> {root_dir}")
        if not dry_run:
            shutil.move(src, dst)

    if not dry_run:
        try:
            os.rmdir(group_dir)
            print(f"[Group {i+1}] Removed empty folder")
        except OSError:
            print(f"[Group {i+1}] Could not remove folder (not empty?)")
    else:
        print(f"[Group {i+1}] Would remove empty folder if dry_run was False")

print("Dry run complete." if dry_run else "Done restoring patient directories to root.")
