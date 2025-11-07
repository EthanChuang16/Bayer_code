import os
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

def find_series_folders(root_path):
  #walk through root path, yield directories that contain DIOCM files 
  #not going recursively to go faster, guard against non dcm files
  series_folders = []
  for patient_id in os.listdir(root_path):
    patient_path = os.path.join(root_path, patient_id)
    if not os.path.isdir(patient_path):
      continue 
    for series_name in os.listdir(patient_path):
      series_path = os.path.join(patient_path, series_name)
      if not os.path.isdir(series_path):
        continue 
      if any(f.lower().endswith(".dcm") for f in os.listdir(series_path)):
        series_folders.append(series_path)

  return series_folders

#calls DICOM_Anon.py on a given series folder and captures its output
def anonymize_series(series_path):
  #call DICOM_Anon.py on a single series folder 
  cmd = [sys.executable, "DICOM_Anon.py", series_path]
  try:
    #run script and capture output 
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return (series_path, True, result.stdout)
  except subprocess.CalledProcessError as e:
    return (series_path, False, e.stderr)

#main logic that parallelizes the anonymization across series folders
def main(root_dir, max_workers=4):
  series_folders = list(find_series_folders(root_dir))
  print(f"[INFO] Found {len(series_folders)} series folders to anonymize in {root_dir}\n")
  
  with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {executor.submit(anonymize_series, sp): sp for sp in series_folders}

    completed = 0

    for future in as_completed(futures):
      series_path = futures[future]
      try:
        path, success, output = future.result()
        patient_id = os.path.basename(os.path.dirname(path))
        series_name = os.path.basename(path)
        completed += 1

        if success:
          print(f"[{completed}/{len(series_folders)}] SUCCESS: {patient_id}/{series_name}")
        else:
          print(f"[{completed}/{len(series_folders)}] FAILED: {patient_id}/{series_name}")
          print(f"Error: {output.strip()}")

          # Log failure to a txt file at the patient ID level
          failure_log_path = os.path.join(os.path.dirname(path), "anonymize_failures.txt")
          with open(failure_log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"FAILED: {series_name}\n")
            log_file.write(f"Reason: {output.strip()}\n\n")
      except Exception as exc:
        print(f"[ERROR] {series_path} generated as exception: {exc}")

  print("\n[INFO] Anonymization process complete.\n")


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Usage: python batch_anonymize.py <DFCI_Anon_root_path> [max_workers]")
    sys.exit(1)
  root_path = sys.argv[1]
  max_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 4

  if not os.path.isdir(root_path):
    print(f"Error: Provided root path '{root_path}' does not exist or is not a directory.")
    sys.exit(1)

  main(root_path, max_workers)

