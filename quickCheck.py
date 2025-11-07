import os

root_dir = "Z:/DFCI_Anon"
non_groups = [
    d for d in os.listdir(root_dir)
    if os.path.isdir(os.path.join(root_dir, d)) and not d.startswith("group_")
]
print(non_groups)
