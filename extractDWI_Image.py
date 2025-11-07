import DILFunctions
import os, subprocess
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
from skimage import filters
import pydicom
from pydicom import dcmread
import pandas as pd
from pydicom.tag import Tag
import traceback


from pathlib import Path
import pandas as pd
from pydicom import dcmread
from pydicom.tag import Tag
import ast

#df = pd.read_csv(os.path.join('D:\\MGHMRI', 'DWI_ZIncV3.csv'))
df = pd.read_csv(os.path.join('D:\\MGHMRI', 'DWI_ZInc_Pass2_mod.csv'))
#df = df[df['NumVolumes'] ==14 ]
#df = df[df['PatientID'] == 2164422]
#df = df[df['PatientID'] == 2837626]

#Exceptions
#2164422: Series 12. Two embedded series/
#2837626: NaN. Present in .xls
#3148816: NaN. Present in .xls
#3836137: Series 12. Excluded
#5627218: SEries 15. Two series numbers.

#Pass 2
#1831516 not exist
#1940548 not exist
#2164422; Cannot reshape array
#3673133: Images look weird, but OK. Verified DICOM.
#5465555: Does not exist
#5487249: Does not exist
#5489923: Does not exist
#5627218: Cannot reshape
#5964237: Cannot reshape
#6256821: Artifact over prostate: Exclude


#Pass3
#2164422; Cannot reshape array
#5465555: Cannot reshape array. Missing
#5627218: Cannot reshape array

#Pass4
#1076586: Cut off top

#Pass5
#Fiducial 0797941
#3382892: Cut off on bottom

baseDir = 'D:\\MGHMRI_Proc'
sourceDir = os.path.join(baseDir,'DWI2')

targetDir = os.path.join(baseDir,'DWI_Extract2')
if not(os.path.isdir(targetDir)):
  os.mkdir(targetDir)

targetDirFig = os.path.join(baseDir,'DWI_Extract2_Fig')
if not(os.path.isdir(targetDirFig)):
  os.mkdir(targetDirFig)



print('Hold')
for _, row in df.iterrows():
    mrn = str(row['PatientID']).zfill(7)
    seriesNumber = row.get('SeriesNumber')

    if pd.isna(row['SlicesPerVolume']):
#    if pd.isna(seriesNumber):
        #print('No slices per volume for ', mrn)
        continue

    seriesNumber = int(seriesNumber)
    #print(f"Patient ID: {mrn} | Series number: {seriesNumber}")

    try:
      figName = os.path.join(targetDirFig, mrn + '.png')
      outputName = os.path.join(targetDir, mrn + '.nii.gz')

      if not (os.path.isfile(figName)):
        print(f"Patient ID: {mrn} | Series number: {seriesNumber}")
        slicesPerVolume = int(row['SlicesPerVolume'])
        numVolumes = int(row['NumVolumes'])
        numIncreasing = int(row['Increasing'])
        numDecreasing = int(row['Decreasing'])

        bval_list = ast.literal_eval(row['Bvals'])
        GradX_list = ast.literal_eval(row['GradX'])
        GradY_list = ast.literal_eval(row['GradX'])
        GradZ_list = ast.literal_eval(row['GradX'])

        imgName = os.path.join(sourceDir, mrn + '.nii.gz')
        imgsitk, img = DILFunctions.readImageFcn(imgName)
        img_shape = img.shape

        img_reshaped = img.reshape(numVolumes, slicesPerVolume, img_shape[1], img_shape[2])
        #print('Initial shape: ', img_shape, ' Reshaped: ', img_reshaped.shape)

        bval_max = max(bval_list)
        bval_max_indices = [i for i, val in enumerate(bval_list) if val == bval_max]

        # Gradient images. Average all together


        if (len(bval_max_indices) == 1):
          img_reshaped_bval_max = img_reshaped[bval_max_indices, :, :, :]
          img_reshaped_bval_max_select = np.squeeze(img_reshaped_bval_max)
        elif (len(bval_max_indices) == 12):
          #print('Tensor images. Averaging indices')
          #print(GradX_list)
          #print(GradY_list)
          #print(GradZ_list)
          img_reshaped_bval_max = img_reshaped[bval_max_indices, :, :, :]
          img_reshaped_bval_max_select = np.mean(img_reshaped_bval_max, axis=0)
        else:
         # print('Length greater than 2. Taking last element')
          img_reshaped_bval_max_select = np.squeeze(img_reshaped[bval_max_indices[0], :, :, :])

        # Flip
        if (numVolumes > 1 and numDecreasing > numIncreasing):
          img_reshaped_bval_max_select = np.flip(img_reshaped_bval_max_select, axis=0)
         # print('Flipping')

        img_reshaped_bval_max_select_sitk = sitk.GetImageFromArray(img_reshaped_bval_max_select)
        img_reshaped_bval_max_select_sitk.SetOrigin(imgsitk.GetOrigin())
        img_reshaped_bval_max_select_sitk.SetDirection(imgsitk.GetDirection())


        sitk.WriteImage(img_reshaped_bval_max_select_sitk, outputName)

        DILFunctions.plotimgOnly(img_reshaped_bval_max_select_sitk, figName, 3)

    except Exception as e:
        print(f"  Error processing MRN {mrn}: {e}")
        traceback.print_exc()