import os, shutil, datetime
import pandas as pd

# Copy MRI files from Mad3 onto Desktop based on characteristics of the directory.

sourceDir = 'Z:\\'
os.chdir(sourceDir)

#t2check = ['AX_T2']
#dwicheck = ['DWI_1400__TR']#, 'Ax_DWI_FOCUS_1400__5FOV']
#adccheck = ['DWI_1400__ADC']#, 'Apparent_D_nt__mm2_s_', 'ADC']

#excludecheck = ['iCAD', 'cor', 'sag', 't1', 'localizer', 't2', 'dcad', 'dynamic', 'dynacad', 'screen', 'post', '__FA', 'ProstateSegReport', 'LAVA', 'SSFSE', 'EXP', 'ZERO_B', '5__Ax_DIFFUSION']
excludecheck = ['Dyn', 'TEST', 'Synthet', 'Plane_Loc', 'iCAD', 'cor', 'sag', 't1', 'localizer', 't2', 'dcad', 'dynamic', 'dynacad', 'screen', 'post', '__FA', 'ProstateSegReport', 'LAVA', 'SSFSE', 'EXP', 'ZERO_B', '5__Ax_DIFFUSION']

#includecheck = ['Apparent']
targetDir = 'D:\\MGHMRI'

#csv_filename = os.path.join(targetDir, 'missing_ADC_DWI.csv') # After making adjustments below.
#csv_filename = os.path.join(targetDir, 'missing_DWI_SignaPremier.csv') # After making adjustments below.
#csv_filename = os.path.join(targetDir, 'missing_DWI_SignaHDxt.csv') # After making adjustments below.
#csv_filename = os.path.join(targetDir, 'missing_ADC_Discovery.csv') # After making adjustments below.
csv_filename = os.path.join(targetDir, 'missing_ADC_FinalCheck.csv') # After making adjustments below.
df = pd.read_csv(csv_filename)

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
                        #if (any([w.lower() in s3.lower() for w in includecheck])):
                          sourceDirFullName = os.path.join(sourceDir, mrn_padded, s1, s2, s3)
                          targetDirFullName = os.path.join(targetDir, mrn_padded, s1, s2, s3)

                          print('Identified: ', sourceDirFullName, ' to: ', targetDirFullName)
                          if not(os.path.isdir(targetDirFullName)):
                            print('Copying')
                            shutil.copytree(sourceDirFullName, targetDirFullName)
                          else:
                            print('Skipping')
    except Exception as e:
        print(f"Error processing {mrn}: {e}")
        continue

