import os
import shutil


base_dir = r'Z:\DFCI'

# List of patient directories to remove
dirs_to_remove = [
    "41360769",
    "41815366",
    "21792650",
    "13461231",
    "43504653",
    "20583241",
    "43653773",
    "38967535",
    "43965961",
    "23801772",
    "38810578",
    "19185578",
    "44069151",
    "12686622",
    "28017465",
    "16844862",
    "33337965",
    "12808382",
    "49832561",
    "17677659",
    "09654187",
    "43466366"
]

for dir_name in dirs_to_remove:
    full_path = os.path.join(base_dir, dir_name)
    if os.path.isdir(full_path):
        try:
            shutil.rmtree(full_path)
            print(f"Removed directory: {full_path}")
        except Exception as e:
            print(f"Failed to remove {full_path}: {e}")
    else:
        print(f"Directory not found, skipping: {full_path}")
