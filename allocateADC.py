import os, shutil, csv
import pandas as pd
import DILFunctions

# First ran subdirectories_T2.pynb from D:\MGHNotes

sourceDir = 'D:\\MGHMRI'

targetDirImg = 'D:\\MGHMRI_Proc\\ADC2'
if (not(os.path.isdir(targetDirImg))):
  os.mkdir(targetDirImg)

targetDirFig = 'D:\\MGHMRI_Proc\\ADC2_Fig'
if (not(os.path.isdir(targetDirFig))):
  os.mkdir(targetDirFig)

#csv_filename = os.path.join(sourceDir, 'subdirectories_ADC_mod_Edited.csv') # After making adjustments below.
csv_filename = os.path.join(sourceDir, 'subdirectories_ADC_mod_Edited_Pass2.csv') # After making adjustments below.
ct = 0
os.chdir(sourceDir)

dirname = os.listdir(sourceDir)

df = pd.read_csv(csv_filename)


#No change needed.


#Alternate series
#0990031: Very grainy?

#Signa HDxt images not good
#1368495, 1369113: Distortion from rectal gas? Not in report.
#1379523: Set to -256. Switch to 10 and 1001
#1989707: Switch to Series 14 and 15
#2854728: Switch to 1153 (otherwise numbers so small)
#3003920: Switch to 1103 ADC and 1100_DWI
#3241555: Discovery MR750w (Apparent) looks badl.
#4145654: Change to 96 (DWI) and 97 (ADC)
#5107054: Synthetic (grainy)
#5571430: Switch to series 11 (DWI) and 1100 (ADC)
#6321054: Rectal gas
#6599399: rectal gas

#Ineligible:
#1069827: Very grainy. Discovery. Apparent. Set to -256
#1336625; Prior RP
#1406917: Hip artifact
#1437272: Fiducial markers
#1454989: No ADC.
#1552736. No ADC image signal
#1627003. ADC zeroed out.
#1787845. ADC zeroed out.
#1924001. Hip artifact
#1995432. Bilateral hip implants
#2044447: Hip implant left
#2105563: Hip implant. Prostate still visible.
#2260819: Hip implant. Prostate still visible.
#2309183: Prostate zeroed out.
#All Avanto images.
#2402747: Hip artifact severe.
#2416928: Hip implant. Prostate still visible.
#2445547: Severe hip artifact
#2474023: Severe hip artifact
#2480124: Coronal ADC
#2514196: Severe hip artifact (prostate still visible)
#2719484: Weird looking image with 850. Series 1050 looks good, but no series 10 (DWI)
#2939099: Hip artifact bilateral.
#2949917: right hip artifact
#3025494: Hip artifact (prostate visible); bladderCa
#3086432: Hip artifact (severe)
#3186981: HIp artifact (top prostate)
#3265878: Hip artifact (bilateral)
#3395555: Hip artifact (left; prostate visible)
#3404098: ADC zeroed out
#3422380: TrioTim bad
#3426655: Severe artifact. MR DISCOVERY 750w
#3427964: Hip artifact (prostate visible)
#3431242: Hip artifact (right)
#3448710: Severe bilateral artifact
#3517151: Severe artifact
#3529879: ADC zeroed out
#3684563: ADC zeroed out
#4049279: ADC zeroed out/ prior RP
#4318298: ADC cut off
#4384515: Severe artifact
#4477169: Left hip artifact/Avanto
#4626090: Zeroed out over little prostate
#4671656: Hip artifact
#4727524: Hip artifact
#4821095: Hip artifact (prostate visible)
#4937529: Hip artifact (severe)
#5102168: Hip artifact (bilateral)
#5253998: HIp artifact (left)
#5356889: ADC zeroed out
#5511928: ADC artifact severe
#5539856: Bilateral artifact hip
#5559026: Severe right hip artifact
#5561149: Hip artifact (right)
#5601391: ADC zeroed out
#5738374: Hip artifact (right)
#5787842: Bilateral hip artifact
#5922902: Hip artifact (right)
#5933287: Hip artifact (right)
#6028649: Hip artifact (right)
#6638567: Hip artifact (prostate visible; left)

# Pass 2
#0990031: Exclude due to artifact through center of image.
#1066206: Focus image non-diagnostic
#1352586: No focus ADC image.
#1473287: Hip artifact
#1793820: no focucs ADC image
#1856783: no focus ADC image
#3647292:No focus ADC image
#5235247: No focus ADC image
#5598910: No focus ADC image
#5649439: No focus ADC image
#6542545: Wide, but mentions focus. Eliminated
#6764227: Wide, but mentions focus. Eliminated


#df = df[df['PatientID'] == 5957173]

for index, row in df.iterrows():
  mrn = str(row['PatientID'])
  mrn_padded = mrn.zfill(7)

#  if pd.notna(row['ADCMatches_filter_series2']):
  if (row['Exclude'] == 0): # O
    seriesNumber = int(row['ADCMatches_filter_series2'])
    print('  index: ', ct)
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
        figName = os.path.join(targetDirFig, mrn_padded + '.png')
        DILFunctions.plotimgOnly(imgsitk, figName, 5)

    else:
      print('No match')
  else:
    seriesNumber = None  # Or handle it some other way
    print('No series number available')


