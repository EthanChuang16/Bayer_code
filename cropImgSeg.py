import os
import DILFunctions
import pandas as pd
baseDir = 'D:\\MGHMRI_Proc'

#imgDir = ['DWI3', 'ADC', 'T2',]
#segDirList = ['DWI3_seg_clean', 'DWI3_seg_clean', 'DWI3_seg_clean',]

#imgDir = ['DWI_Extract2_Info_Img',]
#segDirList = ['DWI_Extract2_Info_Seg_Combined',]

imgDir = ['ADC2', 'DWI_Extract2_Info_Img']
segDirList = ['DWI_Extract2_Info_Seg_Combined','DWI_Extract2_Info_Seg_Combined']

#imgDir = ['T2',]
#segDirList = ['T2_Seg',]

#imgDir = ['ADC2',]
#segDirList = ['T2_Seg',]
suffix = '_crop'
#suffix = '_T2Template_crop'

os.chdir(baseDir)
df = pd.read_csv(os.path.join('D:\\MGHMRI', 'subdirectories_ADC_mod_Edited_Pass2.csv'))
df = df[df['Exclude'] == 0]
df = df[df['PatientID'] == 3161777]


newSize = (128, 128, 20)

#Swap: All ERCs

for cti, i in enumerate(imgDir):
  segDir = segDirList[cti]
  cropDir = i + suffix
  if not (os.path.isdir(cropDir)):
    os.mkdir(cropDir)
  else:
    print('Crop directory already present')

  cropDirFig = i + suffix + '_Fig'
  if not (os.path.isdir(cropDirFig)):
    os.mkdir(cropDirFig)
  else:
    print('Crop directory fig already present')

  segcropDir = cropDir + '_Seg'
  if not (os.path.isdir(segcropDir)):
    os.mkdir(segcropDir)
  else:
    print('Seg Crop directory fig already present')


  for index, row in df.iterrows():
    mrn = str(row['PatientID'])
    mrn_padded = mrn.zfill(7)
    fname = mrn_padded + '.nii.gz'
    fullimgname = os.path.join(baseDir, i, fname)

    if  (os.path.isfile(os.path.join(cropDirFig, mrn_padded + '.png'))):
      print('Analyzing: ', fullimgname)
      imgsitk, img = DILFunctions.readImageFcn(fullimgname)

      newSpacing = (0.7031, 0.7031, imgsitk.GetSpacing()[2])
      #if (cropDir == 'DWI3_crop'):
      DILFunctions.cropImageOnly(i, fname, segDir, fname, cropDir, fname, newSize, newSpacing) # Crop image. No template.
      #else:
      #  templateName = os.path.join(baseDir, 'DWI3_crop', imgNameList[ct])
      #  DILFunctions.cropImageOnly(i, imgNameList[ct], segDir, imgNameList[ct], cropDir, imgNameList[ct], newSize, newSpacing, templateName = templateName)
      print('Cropped: ', fname, ' NewSize: ', newSize, ' NewSpacing: ', newSpacing)

      DILFunctions.cropStructOnly(cropDir, fname, segDir, fname, segcropDir, fname)

      cropimgsitk, cropimg = DILFunctions.readImageFcn(os.path.join(baseDir, cropDir, fname))
      cropsegsitk, cropseg = DILFunctions.readImageFcn(os.path.join(baseDir, segcropDir, fname))

      figName = os.path.join(cropDirFig, fname.split('.')[0] + '.png')

      DILFunctions.plotimgmask2(cropsegsitk, cropimgsitk, figName)