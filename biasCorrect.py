import os, shutil
import csv
import numpy as np
import pandas as pd

# Output DICOM header ofor T2, DWC, and ADI into image.
import DILFunctions

baseDir = 'D:\\MGHMRI_Proc'

#modDir = ['ADC',  'DWI', 'T2']
modDir = ['DWI_Extract2_Info_Img_crop', 'T2_crop']

ADCfile = os.listdir(baseDir)

df = pd.read_csv(os.path.join('D:\\MGHMRI', 'DWIDicom.csv'))

condition_figname = 'ERC'
condition = df['ReceiveCoilName']=='ATDTORSO'#'Signa HDxt'#

#df_print = df[condition]

patient_list = [1831516, 3205580]
df_print = df[df['PatientID'].isin(patient_list)]

for i in modDir:
  fullmodDir = os.path.join(baseDir, i, 'toDelete')
  if not (os.path.isdir(fullmodDir)):
    os.mkdir(fullmodDir)
    print('Creating modDir: ', fullmodDir)
  else:
    print('modDir already present: ', fullmodDir)

for index, row in df_print.iterrows():
  mrn = str(row['PatientID'])
  mrn_padded = mrn.zfill(7)

  for i in modDir:
    sourceFile = os.path.join(baseDir, i, mrn_padded + '.nii.gz')

    # Copy source to toDelete directory
    targetFile = os.path.join(baseDir, i, 'toDelete', mrn_padded + '.nii.gz')
    print('Copying: ', sourceFile, ' to: ', targetFile)
    if (os.path.isfile(sourceFile)):
      shutil.copy(sourceFile, targetFile)
    else:
      print('Directory not found')

    #Write bias corrected file into source
    DILFunctions.biasCorrectSourceTarget(targetFile, sourceFile)