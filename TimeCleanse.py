import os
import re

# Path to the root directory containing all patient ID directories
base_dir = r"Z:\DFCI"
# txt file
output_log = r"Z:\PythonScripts\NewSeriesNames.txt"


# Open the output file for writing
with open(output_log, 'w') as f:
    f.write("Patient ID | Original Series Name --> Proposed New Series Name\n")

    # iterate patient ids
    for patient_id in os.listdir(base_dir):
        patient_path = os.path.join(base_dir, patient_id)
        if not os.path.isdir(patient_path):
            continue

        print(f"Processesing patient ID: {patient_id}")

        # iterate Exam directories
        exam_dirs = [d for d in os.listdir(patient_path)
                     if os.path.isdir(os.path.join(patient_path, d))]

        # Only continue if exactly one subdirectory exists
        if len(exam_dirs) != 1:
            continue


        # Path to the MR directory
        exam_path = os.path.join(patient_path, exam_dirs[0])
        mr_path = os.path.join(exam_path, "MR")
        if not os.path.isdir(mr_path):
            continue

        # Loop through series 
        for series in os.listdir(mr_path):
            series_path = os.path.join(mr_path, series)
            if not os.path.isdir(series_path):
                continue

            if "EST" in series or "EDT" in series:
                # Remove time-related suffix, e.g., _24_31_EDT
                new_series = re.sub(r"(_\d{1,2}_\d{1,2}_(EDT|EST))", "", series)

                if new_series != series:
                    new_path = os.path.join(mr_path, new_series)

                    try:
                        os.rename(series_path, new_path)
                        f.write(f"{patient_id} | {series} --> {new_series}\n")
                    except Exception as e:
                        print(f"Failed to rename {series} in {patient_id}: {e}")
    
                


print(f"Done. Results written to {output_log}")
