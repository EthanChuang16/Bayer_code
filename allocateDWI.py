import os, shutil, csv
import pandas as pd
import DILFunctions

# Copy MRI files from Mad3 onto Desktop based on characteristics of the filename.

sourceDir = 'D:\\MGHMRI'

targetDirImg = 'D:\\MGHMRI_Proc\\DWI2'
if (not(os.path.isdir(targetDirImg))):
  os.mkdir(targetDirImg)

#targetDirFig = 'D:\\MGHMRI_Proc\\DWI2_Fig'
#if (not(os.path.isdir(targetDirFig))):
#  os.mkdir(targetDirFig)


dirname = os.listdir(sourceDir)

#csv_filename = os.path.join(sourceDir, 'subdirectories_ADC_mod_Edited.csv') # After making adjustments below.
#csv_filename = os.path.join(sourceDir, 'subdirectories_ADC_mod_Edited_Pass1.csv') # After making adjustments below.
#csv_filename = os.path.join(sourceDir, 'subdirectories_ADC_mod_Edited_Pass1_Rerun.csv') # After making adjustments below.
csv_filename = os.path.join(sourceDir, 'subdirectories_ADC_mod_Edited_Pass2.csv') # After making adjustments below.

df = pd.read_csv(csv_filename)
df = df[df['PatientID'] == 2837626]

for index, row in df.iterrows():

  mrn = str(row['PatientID'])
  mrn_padded = mrn.zfill(7)

  #if pd.notna(row['DWIMatches_filter_series2']):
  if (row['Exclude'] == 0):  # O
    seriesNumber = int(row['DWIMatches_filter_series2'])
    print('  index: ', index)
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
      imgTargetName = os.path.join(targetDirImg, mrn_padded + '.nii.gz')
      #if (match):
      if not os.path.isfile(imgTargetName):
        DILFunctions.writeDICOMtoMHD2(imgDCMDir, imgTargetName)

        # Print figure
        imgsitk, img = DILFunctions.readImageFcn(imgTargetName)
        #figName = os.path.join(targetDirFig, mrn_padded + '.png')
        #DILFunctions.plotimgOnly(imgsitk, figName, 5)

    else:
      print('No match')
  else:
    seriesNumber = None  # Or handle it some other way
    print('No series number available')

#with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
#  csvwriter = csv.writer(csvfile)

#  for ct in range(0, len(dirname)):
#    d = dirname[ct]
#    print('-------------------------------------------------')
#    print('  Count: ', ct)
#    print('  Patient ID: ', d)
#    subdirectories = []
#    subdirectories.append(d)
#    for s1 in os.listdir(os.path.join(baseTargetDir, d)):
#      if (any([w in s1 for w in dwicheck])):
#        if not ('ADC' in s1):
#          if not ('PU' in s1):
#            if not ('18FOV' in s1):
#              subdirectories.append(s1)

#    csvwriter.writerow(subdirectories)

#    if (len(subdirectories) == 2):
#      imgTxtName = os.path.join(saveDir, d + '.nii.gz')
#      #DILFunctions.writeDICOMtoMHD2(os.path.join(d, subdirectories[1]), imgTxtName)
#      imgsitk, img = DILFunctions.readImageFcn(imgTxtName)
#      #figName = os.path.join(saveFigDir, d + '.png')
#      #DILFunctions.plotimgOnly(imgsitk, figName, 3)
#    else:
#      for ctg in range(1, len(subdirectories)):
#        imgTxtName = os.path.join(saveDir, d + '.' + subdirectories[ctg] + '.nii.gz')
#        #DILFunctions.writeDICOMtoMHD2(os.path.join(d, subdirectories[ctg]), imgTxtName)
#        imgsitk, img = DILFunctions.readImageFcn(imgTxtName)
#        #figName = os.path.join(saveFigDir, d + '.' + subdirectories[ctg] + '.png')
#        #DILFunctions.plotimgOnly(imgsitk, figName, 3)


'''
dwiname = os.listdir(saveDir)

for ct in range(729, len(dwiname)):
  imgname = dwiname[ct]
  bvalname = os.path.join(saveDir, imgname)
  newbvalname = os.path.join(saveDir2, imgname)
  DILFunctions.extractBvalFilterSimple(bvalname, newbvalname, flip = 1)
  imgsitk, img = DILFunctions.readImageFcn(newbvalname)
  figName = os.path.join(saveFigDir, imgname.split('.nii.gz')[0] + '.png')
  DILFunctions.plotimgOnly(imgsitk, figName, 3)
'''

