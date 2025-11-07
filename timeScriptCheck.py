import os

# Path
base_dir = r"Z:\DFCI"
# Output file for any series that still contain EDT/EST
output_log = r"Z:\PythonScripts\RemainingTimeSeries.txt"

# Open the output log
with open(output_log, 'w') as f:
    f.write("Remaining series with EDT/EST in name:\n")

    # Iterate through patient IDs
    for patient_id in os.listdir(base_dir):
        patient_path = os.path.join(base_dir, patient_id)
        if not os.path.isdir(patient_path):
            continue

        # Get exam directories (usually just one)
        exam_dirs = [d for d in os.listdir(patient_path)
                     if os.path.isdir(os.path.join(patient_path, d))]

        for exam in exam_dirs:
            exam_path = os.path.join(patient_path, exam)
            mr_path = os.path.join(exam_path, "MR")

            if not os.path.isdir(mr_path):
                continue

            # Check series folders for "EDT" or "EST"
            for series in os.listdir(mr_path):
                if ("EDT" in series or "EST" in series):
                    f.write(f"{patient_id} | {series}\n")
                    print(f"Found: {patient_id} | {series}")

print(f"Check complete. Results written to {output_log}")
