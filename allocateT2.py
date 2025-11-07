import os, shutil, csv
import pandas as pd
import DILFunctions

# First ran subdirectories_T2.pynb from D:\MGHNotes

sourceDir = 'D:\\MGHMRI'

targetDirImg = 'D:\\MGHMRI_Proc\\T2'
targetDirFig = 'D:\\MGHMRI_Proc\\T2_Fig'

#csv_filename = os.path.join(sourceDir, 'subdirectories_T2_fin.csv')
csv_filename = os.path.join(sourceDir, 'subdirectories_T2_fin_mod.csv') # After making adjustments below.
os.chdir(sourceDir)

dirname = os.listdir(sourceDir)

df = pd.read_csv(csv_filename)
ct = 0

#No change needed.
#1271225: Low res. No other sequence available.
#1704314: Large patient, tilted
#2468413: Low res. No other sequence available.
#2917651: Low res. No other sequence available.
#4145654: Only 10 slices. No other sequences available.
#4560413: Low res. No other sequence avaialble.
#5548425: Utricle cyst

#Alternate series
#2480124: Coronal. Use series 2
#3126972: Low res. Use series 13
#5305707: Post RP: Downloaded pre-RP MRI 9/5/2013. Use series 1 (AxT2)
#5307726: Fat sat? Use series 9
#5663059: Sagittal. Use series 6
#5957173: Low res. Use series 7


#Ineligible:
#0988707: TURP. Post-RP. Ineligible
#5559026: No prostate? Prior-RT with abscess. Ineligible.
#5867321: No prostate? Post-RP. Ineligible
#6089406: No prostate? Post-RP. Ineligible
#5016729: Large prostate growth, cystic?
#5320881: Foley. Prior brachytherapy
#5143080: Not T2 sequence: N1
#1457748: Sagital instead of axial. No T2

for index, row in df.iterrows():
  mrn = str(row['PatientID'])
  mrn_padded = mrn.zfill(7)

  seriesName = row['AxialT2_final']
  print('  index: ', ct)
  print('  Patient ID: ', mrn, ' Series name: ', seriesName)

  # Find name of directory
  subdir1 = os.listdir(os.path.join(sourceDir, mrn_padded))[0]
  subdir2 = 'MR'

  #os.path.listdir  seriesName = row['AxialT2_final']
  imgDCMDir = os.path.join(sourceDir, mrn_padded, subdir1, subdir2, seriesName)
  imgTargetName = os.path.join(targetDirImg, mrn_padded + '.nii.gz')
  #if not os.path.isfile(imgTargetName):
  a = True
  if (a):
    DILFunctions.writeDICOMtoMHD2(imgDCMDir, imgTargetName)

    # Print figure
    imgsitk, img = DILFunctions.readImageFcn(imgTargetName)
    figName = os.path.join(targetDirFig, mrn_padded + '.png')
    DILFunctions.plotimgOnly(imgsitk, figName, 5)

  ct = ct + 1
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
#      if (any([w in s1 for w in t2check])):
#        subdirectories.append(s1)

#    csvwriter.writerow(subdirectories)

#  if (len(subdirectories) == 2):
#    imgTxtName = os.path.join(targetDirImg, d + '.nii.gz')
#    DILFunctions.writeDICOMtoMHD2(os.path.join(d, subdirectories[1]), imgTxtName)
#    imgsitk, img = DILFunctions.readImageFcn(imgTxtName)
#    figName = os.path.join(saveFigDir, d + '.png')
#    DILFunctions.plotimgOnly(imgsitk, figName, 5)
#
#  else:
#    for ctg in range(1, len(subdirectories)):
#      imgTxtName = os.path.join(targetDirImg, d + '.' + subdirectories[ctg] + '.nii.gz')
#      #DILFunctions.writeDICOMtoMHD2(os.path.join(d, subdirectories[ctg]), imgTxtName)
#      imgsitk, img = DILFunctions.readImageFcn(imgTxtName)
#      figName = os.path.join(saveFigDir, d + '.' + subdirectories[ctg] + '.png')
#      DILFunctions.plotimgOnly(imgsitk, figName, 5)

