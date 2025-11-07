import os
import pandas as pd

base_target_dir = 'D:\\MGHMRI'

out_filename = os.path.join(base_target_dir, 'subdirectories_add_missing_adc_dwi_PremierFocus_HDxt_Discovery.csv')

patient_ids = []
subdir_lists = []

ptlist = [d for d in os.listdir(base_target_dir)
          if os.path.isdir(os.path.join(base_target_dir, d))]

for patient_id in ptlist:
    subdirs = []
    patient_path = os.path.join(base_target_dir, patient_id)

    try:
        for s1 in os.listdir(patient_path):
            s1_path = os.path.join(patient_path, s1)
            if not os.path.isdir(s1_path):
                continue
            for s2 in os.listdir(s1_path):
                s2_path = os.path.join(s1_path, s2)
                if not os.path.isdir(s2_path):
                    continue
                for s3 in os.listdir(s2_path):
                    s3_path = os.path.join(s2_path, s3)
                    if os.path.isdir(s3_path):
                        subdirs.append(s3)
    except Exception as e:
        print(f"Error processing {patient_id}: {e}")
        continue

    patient_ids.append(patient_id)
    subdir_lists.append(subdirs)

# Create the DataFrame
df = pd.DataFrame({
    "PatientID": patient_ids,
    "Subdirectories": subdir_lists
})

# Display or save
print(df.head())
print('Writing: ', out_filename)
df.to_csv(out_filename)