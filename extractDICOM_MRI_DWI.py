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

df = pd.read_csv(os.path.join(sourceDir, 'subdirectories_ADC_mod_Edited_Pass2.csv'))
outname = os.path.join(sourceDir, 'DWIDicom.csv')

dcmfilesArr = []

for index, row in df.iterrows():
  mrn = str(row['PatientID'])
  mrn_padded = mrn.zfill(7)

#  if pd.notna(row['DWIMatches_filter_series2']):
  if (row['Exclude'] == 0):  # O
    seriesNumber = int(row['DWIMatches_filter_series2'])
    print('  Patient ID: ', mrn, ' Series number: ', seriesNumber)

    # Find name of directory
    subdir1 = os.listdir(os.path.join(sourceDir, mrn_padded))[0]
    subdir2 = 'MR'
    mrnDirListName = os.path.join(sourceDir, mrn_padded, subdir1, subdir2)

    mrnDICOM_List = os.listdir(mrnDirListName)

    match = next((s for s in mrnDICOM_List if str(s).startswith(f'{seriesNumber}_')), None)
    if (match):
      seriesName = match
      imgDCMDir = os.path.join(sourceDir, mrn_padded, subdir1, subdir2, seriesName)

      dcmfiles = [f for f in os.listdir(imgDCMDir) if f.endswith('.dcm')]
      print('   Num DCM files: ', len(dcmfiles))
      if len(dcmfiles) > 0:
        dcmfullfilename = os.path.join(imgDCMDir, dcmfiles[0])
        dcmfilesArr.append(dcmfullfilename)
    else:
      print('No match')
  else:
    seriesNumber = None  # Or handle it some other way
    print('No series number available')

datasets = [dcmread(fn) for fn in dcmfilesArr]
#27; #42, #43, 44

keywords = ["SeriesDate", "Manufacturer", "InstitutionName", "StudyDescription", "SeriesDescription", "ManufacturerModelName",
              "PatientID", "BodyPartExamined", "ReceiveCoilName", "MRReceiveCoilMacro", "SliceThickness", "RepetitionTime", "EchoTime", "MagneticFieldStrength", "SpacingBetweenSlices",
              "ImageOrientationPatient", "PatientPosition", "ProtocolName", "TransmitCoilName", "FlipAngle", "Rows", "Columns", "PixelSpacing"]


data_dict = {
    keyword: [ds.get(keyword) for ds in datasets]
    for keyword in keywords
}

from pydicom.tag import Tag
private_tag = Tag(0x0043, 0x1039)
#data_dict["0043,1039"] = [ds.get(private_tag) for ds in datasets]
data_dict["BVal_GE"] = [ds.get(private_tag).value if ds.get(private_tag) is not None else "" for ds in datasets]


private_tag_siemens = Tag(0x0019, 0x100c)
#data_dict["0019,100c"] = [ds.get(private_tag_siemens) for ds in datasets]
data_dict["BVal_Siemens"] = [ds.get(private_tag_siemens).value if ds.get(private_tag_siemens) is not None else "" for ds in datasets]

df_out = pd.DataFrame(data_dict)

df_out.to_csv(outname)
print('Wrote: ', outname)