import os, shutil
import csv
import numpy as np
import pandas as pd

# Output DICOM header ofor T2, DWC, and ADI into image.
import DILFunctions

baseDir = 'D:\\MGHMRI_Proc'

ADCfile = os.listdir(baseDir)

baseCSVDir = 'D:\\MGHMRI'
df = pd.read_csv(os.path.join('D:\\MGHMRI', 'DWIDicom.csv'))
df_print = df

crop_T2_seg_fig = 'T2_ADCTemplate_crop_seg_Fig'

for index, row in df_print.iterrows():
  mrn = str(row['PatientID'])
  mrn_padded = mrn.zfill(7)
  print(mrn_padded)

  figName = os.path.join(baseDir, crop_T2_seg_fig, mrn_padded + '.png')
  if not ((os.path.isfile(os.path.join(crop_T2_seg_fig)))):
    # ADC -> T2
    ADCProsDir = os.path.join(baseDir, 'ADC2_Info_Seg_Combined_crop')
    ADCDILDir = os.path.join(baseDir, 'ADC2_Info_Seg_Combined_crop')
    ADCImgDir = os.path.join(baseDir, 'ADC2_crop')
    T2RegDir = os.path.join(baseDir, 'Reg_ADC_T2')

    T2ImgDir = os.path.join(baseDir, 'T2_ADCTemplate_crop')
    T2ProsDir = os.path.join(baseDir, 'T2_Seg_crop')

    cropimgsitk, cropimg = DILFunctions.readImageFcn(os.path.join(baseDir, T2ImgDir, fname))

    DILFunctions.plotimgmask2(cropimgsitk, figName, 3)
