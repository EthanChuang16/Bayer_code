import os
import pandas as pd

sourceDir = 'Z:\\'
targetDir = 'D:\\MGHMRI'
csv_filename = os.path.join(targetDir, 'missing_ADC_DWI.csv') # After making adjustments below.
df = pd.read_csv(csv_filename)

out_filename = os.path.join(targetDir, 'missing_ADC_DWI_subdirectories2.csv')

patient_ids = []
subdir_lists = []

excludecheck = ['iCAD', 'cor', 'sag', 't1', 'localizer', 't2', 'dcad', 'dynamic', 'dynacad', 'screen', 'post', '__FA', 'ProstateSegReport', 'LAVA', 'SSFSE', 'EXP']

for index, row in df.iterrows():
    mrn = str(row['PatientID'])
    mrn_padded = mrn.zfill(7)

    print('Processing: ', mrn_padded)
    subdirs = []
    patient_path = os.path.join(sourceDir, mrn_padded)

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
                        if not (any([w.lower() in s3.lower() for w in excludecheck])):
                          subdirs.append(s3)
                          print('Appending: ', s3)
    except Exception as e:
        print(f"Error processing {mrn}: {e}")
        continue

    patient_ids.append(mrn)
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