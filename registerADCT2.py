import os, shutil
import csv
import numpy as np
import pandas as pd

# Output DICOM header ofor T2, DWC, and ADI into image.
import DILFunctions

baseDir = 'D:\\MGHMRI_Proc'

ADCfile = os.listdir(baseDir)

baseCSVDir = 'D:\\MGHMRI'
#df = pd.read_csv(os.path.join('D:\\MGHMRI', 'DWIDicom.csv'))
df = pd.read_csv(os.path.join('D:\\MGHMRI', 'DWIDicom_Mod.csv'))

#condition = df['ReceiveCoilName']=='ATDTORSO'#'Signa HDxt'#
df_print = df#[(df['RedoReg'] == '1')]# & (df['PatientID']>3145176)]

df_print = df_print[df_print['PatientID'] == 3519249]
#Recheck 3205580, 3519249





for index, row in df_print.iterrows():
  mrn = str(row['PatientID'])
  mrn_padded = mrn.zfill(7)
  print(mrn_padded)


    #T2 -> ADC
    #ADCProsDir = os.path.join(baseDir, 'ADC2_Info_Seg_Combined_crop')
    #ADCDILDir = os.path.join(baseDir, 'ADC2_Info_Seg_Combined_crop')
    #T2ImgDir = os.path.join(baseDir, 'T2_crop')
    #T2ProsDir = os.path.join(baseDir, 'T2_Seg_crop')
    #T2RegDir = os.path.join(baseDir, 'Reg_T2_ADC')
    #DILFunctions.registerT2Dir(mrn_padded, ADCProsDir, ADCDILDir, T2ImgDir, T2ProsDir, T2RegDir, deform = 0, sdm = 1)


  # ADC -> T2
  ADCProsDir = os.path.join(baseDir, 'ADC2_Info_Seg_Combined_crop')
  ADCDILDir = os.path.join(baseDir, 'ADC2_Info_Seg_Combined_crop')
  ADCImgDir = os.path.join(baseDir, 'ADC2_crop')
  transformImgDir = os.path.join(baseDir, 'DWI_Extract2_Info_Img_crop')

  if (row['ReceiveCoilName'] == 'ATDTORSO'):
    T2RegDir = os.path.join(baseDir, 'Reg_ADC_T2_ERC_RedoRigid')
  else:
    T2RegDir = os.path.join(baseDir, 'Reg_ADC_T2_NoERC_RedoRigid')

  T2ImgDir = os.path.join(baseDir, 'T2_crop')
  T2ProsDir = os.path.join(baseDir, 'T2_Seg_crop')

  regResultFile = os.path.join(baseDir, T2RegDir, mrn_padded + '.nii.gz')
  if  ((os.path.isfile(os.path.join(regResultFile)))):
    DILFunctions.registerT2Dir(mrn_padded, T2ProsDir, T2ProsDir, ADCImgDir, ADCProsDir, T2RegDir, deform = 0, sdm = 1, transformImgDir = transformImgDir)


  #if (row['ReceiveCoilName'] == 'ATDTORSO'): #Deform if ERC.
  #  DILFunctions.registerT2Dir(mrn_padded, ADCProsDir, ADCDILDir, T2ImgDir, T2ProsDir, T2RegDir, deform = 1, sdm = 1)
  #else:
