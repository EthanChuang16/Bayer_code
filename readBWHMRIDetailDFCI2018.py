import os, csv
import pandas as pd
import numpy as np
import re
#import spacy
#import numerizer

#nlp = spacy.load('en_core_web_sm')
date_pattern = re.compile(r'\d{1,2}/\d{1,2}/\d{4}')
date_pattern2 = re.compile(r'\d{1,2}/\d{1,2}/\d{2}')
#os.chdir('H:\\DILMRI\\DFCI-11234_20230112_164602')
#os.chdir('C:\\Users\\13125\\Documents\\pathReport\\DFCI2018')
os.chdir('Z:\MRI_Report')
# os.chdir('C:\\Users\\13125\\Documents\\pathReport\\MGH2010-2022')

#pathfn ='test3.txt'
pathfn = 'radMRI.txt'

outputfn='testMRI.csv'#'testBWFH.csv'
g = open(outputfn,'w', newline = '')

writer = csv.writer(g, delimiter=',')
writer.writerow(('Report', 'PMRN', 'Date', 'Type', 'PSA', 'BxResults', 'PriorTx', 'ProsVol',\
                 'SV', 'Bladder', 'Rectum', 'LN', 'Bones', \
                 'Imp1', 'Imp2', 'Imp3', 'Imp4', 'Imp5', 'Imp6', \
                 'DIL1Size', 'DIL1PIRADS', 'DIL1Side', 'DIL1Level', 'DIL1Zone', 'DIL1EPE', 'DIL1SV',\
                 'DIL2Size', 'DIL2PIRADS', 'DIL2Side', 'DIL2Level', 'DIL2Zone', 'DIL2EPE', 'DIL2SV',\
                 'DIL3Size', 'DIL3PIRADS', 'DIL3Side', 'DIL3Level', 'DIL3Zone', 'DIL3EPE', 'DIL3SV',\
                 'DIL4Size', 'DIL4PIRADS', 'DIL4Side', 'DIL4Level', 'DIL4Zone', 'DIL4EPE', 'DIL4SV',\
                 'DIL5Size', 'DIL5PIRADS', 'DIL5Side', 'DIL5Level', 'DIL5Zone', 'DIL5EPE', 'DIL5SV'))


numstage = 0
numreport = 0

date_regex = '^(0[1-9]|1[012])[- /.] (0[1-9]|[12][0-9]|3[01])[- /.] (19|20)\d\d$'

side = ['right', 'left']
level = ['base', 'mid', 'apex']
pztz = ['PZpl', 'PZpm', 'PZa', 'TZa', 'TZp']

impCheck = ['NOTE:', 'I, the teaching physician', "report_end", "PI-RADS 1:", "ATTESTATION:", "The Radiologist Diagnostic"]
rectumCheck = ['Rectum:', 'Rectum/sigmoid:', 'Rectum/Colon:', 'Bowel/Rectum:']
boneCheck = ['Bones:', 'Bones/Soft Tissues:', 'Bones and soft tissues:']
mriCheck = ['TRANSITION', 'Seminal']
focalLesionCheck = ['Focal Lesion(s):', 'Focal Lesion:']
pl12Check = ['', 'None']

epeNo = ['no evidence', 'no extraprostatic extension', 'no definite', 'without evidence']
epeYes = ['may represent', 'likely represents', 'associated multifocal', 'focal']
dilRightCheck = ['right']
dilLeftCheck = ['left']
dilBaseCheck = ['base', 'basilar']
dilMidCheck = ['mid']
dilApexCheck = ['apex', 'apical']

def extractNum(index, line):
  val = ''
  if (index in line):
    val = line.split(index)[0].strip().split(' ')[-1]
  return(val)

with open (pathfn, "r") as f:
  line = f.readline()
  header = line.split('|') # Interested in indices 1: EPIC_PMRN, 5: Report_Date_Time, 6: Report_Description
  for line in f:
    fsplit = line.split('|')

    if (len(fsplit) == 10):
      opheader = fsplit
      pmrn = opheader[1]
      rptdate = opheader[5].split(' ')[0]
      rpttype = opheader[6]
      psa = ''; bxResults = ''; priorTx = ''; prosVol = ''; sv = ''; bladder = ''; rectum = ''; lymphNodes = ''; bone = ''

      dilSizeArr = []
      dilPIRADSArr = []
      dilEPEArr = []
      dilSideArr = []
      dilLevelArr = []
      dilZoneArr = []
      dilSVArr = []

    if ('PSA:' in line):
      psa = line.split(':')[1].strip()
    if ('Biopsy results:' in line):
      bxResults = line.split(':')[1].strip()
    if ('Prior therapy:' in line):
      priorTx = line.split(':')[1].strip()
    if ('Prostate Gland Size:' in line):
      if ('volume\n' in line):
        line = f.readline()
      prosVol = extractNum('mL', line)
    if ('Prostate Volume:' in line):
      prosVol = extractNum('mL', line)
    if (any([w in line for w in focalLesionCheck])):
      pl12List = []
      if (len(line.split(':')[1].strip())>1):
        line = line.split(':')[1]
      else:
        line = f.readline() #Read first line

      if (pmrn == '10050514461'):
        print('Hold')

      #if (any([w in line.strip().split(' ')[0].strip() for w in mriCheck])):
      while (not any([w in line.strip().split(' ')[0] for w in mriCheck])):
        pl12 = ''
        #line = f.readline()
        while (line.strip(' ') != '\n'):
#
          pl12 = pl12 + line.strip() + ' '
          line = f.readline()
        #if (pl12.strip() != ''):
        if (not any([w == pl12.strip() for w in pl12Check])):
          pl12List.append(pl12.strip())
        line = f.readline()

      print(pl12List)
      for i in range(0, len(pl12List)):
        dilSize = ''; dilPIRADS = ''; dilEPE = ''; dilSide = ''; dilLevel = ''; dilZone = ''; dilSV = ''

        mrielem = ['cm', 'pi-rads', 'extraprostatic', 'zone', 'seminal']
        ind_mrielem = []
        mrival = []

        pl12 = pl12List[i]
        pl12sentences = re.split('["."][^0-9]', pl12)

        #Eliminate stray sentence that mentions EPE.
        pl12elimstring = 'The lesion is focally markedly hypointense on ADC and markedly hyperintense on high b-value DWI; ? 1.5 cm in greatest dimension, dynamic contrast enhancement is positive, and is circumscribed, homogenous moderate hypointense focus/mass confined to prostate and ? 1.5cm in greatest dimension or definite extraprostatic extension/invasive behavior on T2WI'
        for k in range(0, len(pl12sentences)):
          if (pl12elimstring in pl12sentences[k]):
            pl12sentences[k] = ''

        for j in range(0, len(mrielem)):
          ind_mrielem.append([i for i in pl12sentences if mrielem[j] in i.lower()])
          if (len(ind_mrielem[j]) > 0):
            pl12_lines = ind_mrielem[j][0].split('\n')

            mrielem_j = [i for i in pl12_lines if mrielem[j] in i.lower()]
            mrival.append(mrielem_j[0].strip())
          else:
            mrival.append('')


      #mrielem = ['cm', 'PI-RADS', 'extraprostatic', 'zone', 'seminal']
        if ('cm' in mrival[0]):
          cmstring = mrival[0].split('cm')[0].strip()[-10:]
          if (len(cmstring.split(' x ')) == 2):
            pGS1 = cmstring.split('x')[0].strip()[-3:]
            pGS2 = cmstring.split('x')[1].strip()[0:]
            dilSize = pGS1 + ' x ' + pGS2
          else:
            dilSize = mrival[0].split('cm')[0].strip()[-3:]
        if ('PI-RADS' in mrival[1]):
          dilPIRADS = mrival[1].split('PI-RADS')[1].strip()[0]
        if (any([w in mrival[2] for w in epeNo])):
          dilEPE = 'No'
        else:
          if (any([w in mrival[2] for w in epeYes])):
            dilEPE = 'Yes'
          else:
            dilEPE = mrival[2]
        if (any([w in mrival[3] for w in dilRightCheck])):
          dilSide = 'R'
        else:
          if (any([w in mrival[3] for w in dilLeftCheck])):
            dilSide = 'L'
          else:
            dilSide = mrival[3]
        if (any([w in mrival[3] for w in dilBaseCheck])):
          dilLevel = 'Base'
        else:
          if (any([w in mrival[3] for w in dilMidCheck])):
            dilLevel = 'Mid'
          else:
            if (any([w in mrival[3] for w in dilApexCheck])):
              dilLevel = 'Apex'
            else:
              dilLevel = mrival[3]
        if ('PZ' in mrival[3]):
          dilZone = 'PZ' + mrival[3].split('PZ')[1].split(')')[0]
        else:
          if ('TZ' in mrival[3]):
            dilZone = 'TZ' + mrival[3].split('TZ')[1].split(')')[0]
        dilSV = mrival[4]

        dilSizeArr.append(dilSize);
        dilPIRADSArr.append(dilPIRADS);
        dilEPEArr.append(dilEPE);
        dilSideArr.append(dilSide);
        dilLevelArr.append(dilLevel)
        dilZoneArr.append(dilZone)
        dilSVArr.append(dilSV)

    if ('Seminal Vesicles:' in line):
      sv = line.split(':')[1].strip()
    if ('Bladder:' in line):
      bladder = line.split(':')[1].strip()
    if any([w in line for w in rectumCheck]):
      rectum = line.split(':')[1].strip()
    if ('Lymph Nodes:' in line):
      lymphNodes = line.split(':')[1].strip()
    if any([w in line for w in boneCheck]):
      bone = line.split(':')[1].strip()

    if ("IMPRESSION:\n" in line):
      line = f.readline()
      impList = []
      pl12 = ''

#      if (pmrn == '10044580727'):
#        print("hold")

#      while (not any([w in line.strip().split(' ')[0] for w in impCheck])):
      while (not any([w in line for w in impCheck])):
        pl12 = pl12.strip() + ' ' + line
        if (len(pl12.strip())>1):
          if (pl12.strip()[-1] == '.'):
            impList.append(pl12.strip())
            pl12 = ''
        line = f.readline()

      if(len(impList) == 0):
        impList.append(pl12.strip())

    if "report_end" in line:
      impListLen = len(impList)
      diffimpListLen = 6 - impListLen
      for i in range(0, diffimpListLen):
        impList.append('NA')

      dilListLen = len(dilSizeArr)
      diffdilListLen = 5 - dilListLen
      for i in range(0, diffdilListLen):
        dilSizeArr.append('NA')
        dilPIRADSArr.append('NA')
        dilSideArr.append('NA')
        dilLevelArr.append('NA')
        dilZoneArr.append('NA')
        dilEPEArr.append('NA')
        dilSVArr.append('na')

      print('Report number: ', numreport)

      idlist = list((numreport, pmrn, rptdate, rpttype, psa, bxResults, priorTx, prosVol, \
                     sv, bladder, rectum, lymphNodes, bone, \
                     impList[0], impList[1], impList[2], impList[3], impList[4], impList[5], \
                     dilSizeArr[0], dilPIRADSArr[0], dilSideArr[0], dilLevelArr[0], dilZoneArr[0], dilEPEArr[0], dilSVArr[0], \
                     dilSizeArr[1], dilPIRADSArr[1], dilSideArr[1], dilLevelArr[1], dilZoneArr[1], dilEPEArr[1], dilSVArr[1], \
                     dilSizeArr[2], dilPIRADSArr[2], dilSideArr[2], dilLevelArr[2], dilZoneArr[2], dilEPEArr[2], dilSVArr[2], \
                     dilSizeArr[3], dilPIRADSArr[3], dilSideArr[3], dilLevelArr[3], dilZoneArr[3], dilEPEArr[3], dilSVArr[3], \
                     dilSizeArr[4], dilPIRADSArr[4], dilSideArr[4], dilLevelArr[4], dilZoneArr[4], dilEPEArr[4], dilSVArr[4]))
      writer.writerow(idlist)
      numreport = numreport + 1
      print('------------------------------')
      print('Num Report: ', numreport)
      print('PMRN: ', pmrn, ' Date: ', rptdate)
      print('PSA: ', psa)
      print('PriorTx: ', priorTx)
      print('ProsVol: ', prosVol)
g.close()