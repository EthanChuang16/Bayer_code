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

sourceDir = 'D:\\MGHMRI'

df = pd.read_csv(os.path.join(sourceDir, 'subdirectories_ADC_mod_Edited_Pass1.csv'))
outname = os.path.join(sourceDir, 'DWI_BValInfo.csv')

keywords = ["ImagePositionPatient"]

#def is_increasing(lst):
#  return all(x < y for x, y in zip(lst, lst[1:]))

def count_increasing_decreasing(lst):
  increasing = sum(1 for x, y in zip(lst, lst[1:]) if x < y)
  decreasing = sum(1 for x, y in zip(lst, lst[1:]) if x > y)
  return increasing, decreasing

mrn_arr = []
mriModel_arr = []
mriSeries_arr = []
seriesNum_arr = []
nslice_arr = []
z_possslice_arr = []
bval_arr = []

for index, row in df.iterrows():
  mrn = str(row['PatientID'])
  mrn_padded = mrn.zfill(7)

  mrn_arr.append(mrn)

  if pd.notna(row['DWIMatches_filter_series2']):
    seriesNumber = int(row['DWIMatches_filter_series2'])
    seriesNum_arr.append(seriesNumber)
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
      dcmfiles = sorted(dcmfiles)
      #print(dcmfiles)
      print('   Num DCM files: ', len(dcmfiles))

      ds_slice = [dcmread(os.path.join(imgDCMDir, name)) for name in dcmfiles]
      z_positions_ds_slice = [float(ds.ImagePositionPatient[2]) for ds in ds_slice]
      z_possslice_arr.append(z_positions_ds_slice)
      nslice_value = len(z_positions_ds_slice)
      nslice_arr.append(nslice_value)

      private_tag = Tag(0x0043, 0x1039)
      # data_dict["0043,1039"] = [ds.get(private_tag) for ds in datasets]
      bval_slice = [str(ds.get(private_tag).value) if ds.get(private_tag) is not None else "" for ds in ds_slice]
      bval_arr.append(bval_slice)

      mriModel = ds_slice[0].ManufacturerModelName
      mriModel_arr.append(mriModel)

      mriSeries = ds_slice[0].SeriesDescription
      mriSeries_arr.append(mriSeries)
    else:
      nslice_arr.append(None)
      mriModel_arr.append(None)
      mriSeries_arr.append(None)
      z_possslice_arr.append(None)
      bval_arr.append(None)
      print('No match')
  else:
    seriesNum_arr.append(None)
    mriModel_arr.append(None)
    mriSeries_arr.append(None)
    nslice_arr.append(None)
    z_possslice_arr.append(None)
    bval_arr.append(None)
    # seriesNumber = None  # Or handle it some other way
    print('No series number available')

  dfout = pd.DataFrame({'MRN': mrn_arr, 'SeriesNum': seriesNum_arr, 'ManufacturerModelName': mriModel_arr,
                        'SeriesDescription': mriSeries_arr, 'nslice': nslice_arr, 'zpos': z_possslice_arr,
                        'bval': bval_arr})
  dfout.to_csv(outname)
  # 27; #42, #43, 44

