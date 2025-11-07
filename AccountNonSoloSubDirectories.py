import os

base_target_dir = r'Z:\DFCI'
output_file = r'Z:\PythonScripts\patients_with_multiple_subdirs.txt'

print(f"Scanning all patient directories in: {base_target_dir}")

patients_with_multiple = []

try:
    for name in os.listdir(base_target_dir):
        full_path = os.path.join(base_target_dir, name)
        if not os.path.isdir(full_path):
            continue

        #subdirectories
        subdirs = [d for d in os.listdir(full_path)
                   if os.path.isdir(os.path.join(full_path, d))]

        if len(subdirs) > 1:
            print(f"{name} has {len(subdirs)} subdirectories: {subdirs}")
            patients_with_multiple.append(name)


except Exception as e:
    print(f"Error: {e}")

#write results to txt file
try:
    with open(output_file,'w') as f:
        for pid in patients_with_multiple:
            f.write(f"{pid}\n")
    print(f"Done. {len(patients_with_multiple)} patient IDs saved to {output_file}")
except Exception as e:
    print(f"Failed to write file: {e}")

print("Finished Scan")
print(f"Patients with >1 subdirectory: {len(patients_with_multiple)}")
