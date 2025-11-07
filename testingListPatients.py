import os

# Root directory to scan
base_target_dir = r'Z:\DFCI'

print(f"Scanning directories in: {base_target_dir}")


count = 0


try:
    for name in os.listdir(base_target_dir):
        full_path = os.path.join(base_target_dir, name)
        if os.path.isdir(full_path):
            print(name)
            count += 1
except Exception as e:
    print(f"Error while scanning: {e}")

print(f"\nTotal directories found: {count}")