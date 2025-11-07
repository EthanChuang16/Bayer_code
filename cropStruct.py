import os
import DILFunctions

baseDir = 'D:\\MGHMRI_Proc'

#imgDir = ['DWI3', 'T2', 'ADC']
#segDirList = ['DWI3_seg_clean', 'T2_seg_clean', 'ADC_seg_GTV']

#imgDir = ['T2']
#segDirList = ['T2_Seg']

#imgDir = ['ADC2']
#segDirList = ['ADC2_Info_Seg_Combined']

imgDir = ['T2']
segDirList = ['ADC2_Info_Seg_Combined']
segcropDir = 'T2_ADCTemplate_Seg_crop'

os.chdir(baseDir)

for cti, i in enumerate(imgDir):
  segDir = segDirList[cti]
  cropDir = i + '_crop'

  #segcropDir = segDir + '_Proscrop'
  #segcropDir = segDir + '_crop'
  if not (os.path.isdir(segcropDir)):
    os.mkdir(segcropDir)
  else:
    print('Seg crop directory already present')
  #imgNameList = ['27615327.nii.gz', '28221810.nii.gz']#os.listdir(i)
  imgNameList = os.listdir(i)

  for ct in range(0, len(imgNameList)):
    if (os.path.isfile(os.path.join(cropDir,imgNameList[ct] ))):
      DILFunctions.cropStructOnly(cropDir, imgNameList[ct], segDir, imgNameList[ct], segcropDir, imgNameList[ct])  # Crop prostate


