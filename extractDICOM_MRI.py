import DILFunctions
import os, subprocess
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
from skimage import filters
import pydicom
from pydicom import dcmread
import pandas as pd

sourceDir = 'D:\\MGHMRI'

#df = pd.read_csv(os.path.join(baseDir, 'subdirectoriesDWI_Fin3.csv'))
#outname = 'DWIDicom.csv'

#df = pd.read_csv(os.path.join(baseDir, 'subdirectoriesADC_Fin2.csv'))
#outname = 'ADCDicom.csv'

df = pd.read_csv(os.path.join(sourceDir, 'subdirectories_T2_fin_edit.csv'))
outname = os.path.join(sourceDir, 'T2Dicom.csv')

dcmfilesArr = []

for index, row in df.iterrows():
  mrn = str(row['PatientID'])
  mrn_padded = mrn.zfill(7)

  seriesName = row['AxialT2_final']
  print('  index: ', index)
  print('  Patient ID: ', mrn, ' Series name: ', seriesName)

  # Find name of directory
  subdir1 = os.listdir(os.path.join(sourceDir, mrn_padded))[0]
  subdir2 = 'MR'

  #os.path.listdir  seriesName = row['AxialT2_final']
  imgDCMDir = os.path.join(sourceDir, mrn_padded, subdir1, subdir2, seriesName)

  if (os.path.isdir(imgDCMDir)):
    dcmfiles = [f for f in os.listdir(imgDCMDir) if f.endswith('.dcm')]
    print('   Num DCM files: ', len(dcmfiles))
    if len(dcmfiles) > 0:
      dcmfullfilename = os.path.join(imgDCMDir, dcmfiles[0])
      dcmfilesArr.append(dcmfullfilename)


datasets = [dcmread(fn) for fn in dcmfilesArr]
#27; #42, #43, 44

keywords = ["SeriesDate", "Manufacturer", "InstitutionName", "StudyDescription", "SeriesDescription", "ManufacturerModelName",
              "PatientID", "BodyPartExamined", "SliceThickness", "RepetitionTime", "EchoTime", "MagneticFieldStrength", "SpacingBetweenSlices",
              "ProtocolName", "TransmitCoilName", "FlipAngle", "Rows", "Columns", "PixelSpacing"]


data_dict = {
    keyword: [ds.get(keyword) for ds in datasets]
    for keyword in keywords
}


df_out = pd.DataFrame(data_dict)

df_out.to_csv(outname)
print('Wrote: ', outname)