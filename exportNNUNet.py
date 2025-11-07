# Creates a NNUNet file
# Creates json file
import SimpleITK as sitk
import os, shutil
import pandas as pd
import json
from typing import Tuple
from typing import List
import numpy as np
import random
import DILFunctions

def subfiles(folder: str, join: bool = True, prefix: str = None, suffix: str = None, sort: bool = True) -> List[str]:
  if join:
    l = os.path.join
  else:
    l = lambda x, y: y
  res = [l(folder, i) for i in os.listdir(folder) if os.path.isfile(os.path.join(folder, i))
         and (prefix is None or i.startswith(prefix))
         and (suffix is None or i.endswith(suffix))]
  if sort:
    res.sort()
  return res

def get_identifiers_from_splitted_files(folder: str):
  uniques = np.unique([i[:-12] for i in subfiles(folder, suffix='.nii.gz', join=False)])
  return uniques

def save_json(obj, file: str, indent: int = 4, sort_keys: bool = True) -> None:
  with open(file, 'w') as f:
    json.dump(obj, f, sort_keys=sort_keys, indent=indent)

def generate_dataset_json(output_file: str, imagesTr_dir: str, modalities: Tuple, labels: dict):

  train_identifiers = get_identifiers_from_splitted_files(imagesTr_dir)

  json_dict = {}
  json_dict['channel_names'] = str(modalities)
  json_dict['labels'] = str(labels)

  json_dict['numTraining'] = len(train_identifiers)
  json_dict['file_ending'] = '.nii.gz'

  if not output_file.endswith("dataset.json"):
    print("WARNING: output file name is not dataset.json! This may be intentional or not. You decide. "
              "Proceeding anyways...")
  save_json(json_dict, os.path.join(output_file))

def checkCoordCongruent(idarr, baseDir, modDir):
  for i in idarr:
    print('===============', i)
    # Copy image into directory. If labelOnly = 1, then the image is not copied over.
    for s in range(0, len(modDir)):
      filename = os.path.join(baseDir, modDir[s], str(i) + '.nii.gz')
      imgsitk = sitk.ReadImage(filename)
      print(' Filename: ', filename, ' Origin: ', imgsitk.GetOrigin(), ' Size: ', imgsitk.GetSize(), )

      if (s == 0):
        bvalOrigin = np.array(imgsitk.GetOrigin())
        bvalSize = np.array(imgsitk.GetSize())
        bvalSpacing = np.array(imgsitk.GetSpacing())

      diffOrigin = imgsitk.GetOrigin() - bvalOrigin
      diffSize = imgsitk.GetSize() - bvalSize
      diffSpacing = imgsitk.GetSpacing() - bvalSpacing

      sumDiffOrigin = np.sum(diffOrigin)
      sumDiffSize = np.sum(diffSize)
      sumDiffSpacing = np.sum(diffSpacing)
      print(' sumDiffOrigin: ', sumDiffOrigin, ' sumDiffSize: ', sumDiffSize, ' sumDiffSpacing: ', sumDiffSpacing)


      if (abs(sumDiffOrigin) > 0):
        print('   !!!!!!!!!!Non-zero origin sum: ', sumDiffOrigin)
        oldfilename = filename.split('.')[0] + '.OLD.nii.gz'
        shutil.copy(filename, oldfilename) # Save old filename
        print('   Copied: ', filename, ' to: ', oldfilename)

        print('   Setting new origin: ', bvalOrigin, ' for file: ', filename)
        imgsitk.SetOrigin(bvalOrigin)
        writerFilter.SetFileName(filename)
        writerFilter.Execute(imgsitk)
      if (sumDiffSize > 0):
        print('   !!!!!!!!!!Non-zero size sum: ', sumDiffSize)
      if (abs(sumDiffSpacing) >0):
        print('   **************************Non-zero spacing sum: ', sumDiffSpacing)
        oldfilename = filename.split('.')[0] + '.OLD.nii.gz'
        shutil.copy(filename, oldfilename)  # Save old filename
        print('   Copied: ', filename, ' to: ', oldfilename)

        print('   Setting new spacing: ', bvalSpacing, ' for file: ', filename)
        imgsitk.SetSpacing(bvalSpacing)
        writerFilter.SetFileName(filename)
        writerFilter.Execute(imgsitk)

def copyImageOnly(mrn_str, baseDir, modDir, modIndex, newidarr, outputTrainDir):
  for cti, i in enumerate(mrn_str):
    print('===============', i)

    # Copy image into directory. If labelOnly = 1, then the image is not copied over.
    for s in range(0, len(modDir)):
      filename = os.path.join(baseDir, modDir[s], str(i) + '.nii.gz')

      outFileName = os.path.join(outputTrainDir, newidarr[cti] + '_' +  modIndex[s] + ".nii.gz")

      shutil.copy(filename, outFileName)
      readerFilter.SetFileName(filename)
      imgsitk = readerFilter.Execute()

      print('Origin:', imgsitk.GetOrigin(), ' Size: ', imgsitk.GetSize(), ' Old filename: ', filename, ' New filename:', outFileName)


def copyLabelOnly(mrn_str, baseDir, labelDir, newidarr, outputLabelDir):

  for cti, i in enumerate(mrn_str):
    print('===============', i)
    prosname = os.path.join(baseDir, labelDir[0], str(i) + '.nii.gz')
    dilname = os.path.join(baseDir, labelDir[1], str(i) + '.nii.gz')

    prossitk = sitk.ReadImage(prosname)  # Assume 3D image.

    PZTZsitk = prossitk >=1  # The labels from MONAI-label are flipped. TZ = 2. PZ = 1
    PZsitk = prossitk == 1

    dilsitk = sitk.ReadImage(dilname)
    FinLabelsitk = sitk.Cast(PZTZsitk, sitk.sitkUInt8) + sitk.Cast(PZsitk, sitk.sitkUInt8) + sitk.Cast(dilsitk,sitk.sitkUInt8)*3

    thresholdImageFilter.SetOutsideValue(3)
    thresholdImageFilter.SetUpper(3)
    threshFinLabelsitk = thresholdImageFilter.Execute(FinLabelsitk)

    newthreshFinLabelsitk = threshFinLabelsitk #roiFilter.Execute(threshFinLabelsitk)
    newthreshfinLabel = sitk.GetArrayFromImage(newthreshFinLabelsitk)

    labelFullName = os.path.join(outputLabelDir,  newidarr[cti] + '.nii.gz')
    sitk.WriteImage(newthreshFinLabelsitk, labelFullName)
    print('Origin:', newthreshFinLabelsitk.GetOrigin(), ' Size:', newthreshFinLabelsitk.GetSize(), ' Max label: ', newthreshfinLabel.max(), ' Label filename: ', labelFullName)

readerFilter = sitk.ImageFileReader()
writerFilter = sitk.ImageFileWriter()
thresholdImageFilter = sitk.ThresholdImageFilter()

df = pd.read_csv(os.path.join('D:\\MGHMRI_Proc', 'adt_test_mod052725_poistMerge.csv'))
df2 = df[pd.isna(df['Exclude'])]

baseDir = 'D:\\MGHMRI_Proc'
os.chdir(baseDir)

modDir = ['FinDir\\DWI', 'FinDir\\ADC', 'FinDir\\T2']
modIndex = ('0000', '0001', '0002')
#labelDir = ['DWI3_seg_clean_crop', 'ADC_seg_GTV_crop']

labels = {"background": '0', "Prostate": '1', "DIL": '2'}
channel_names = {"0": 'BVal', "1": 'ADC', "2:": 'T2'}

outputDir = 'export'
outputTrainDir = os.path.join(outputDir, 'imagesTr')
#outputTrainLabelDir = os.path.join(outputDir, 'labelsTr')

if not os.path.isdir(outputDir): os.mkdir(outputDir)
if not os.path.isdir(outputTrainDir): os.mkdir(outputTrainDir)
#if not os.path.isdir(outputTrainLabelDir): os.mkdir(outputTrainLabelDir)

mrn_str = []
for index, row in df2.iterrows():
  mrn = str(row['MRN'])
  mrn_padded = mrn.zfill(7)
  print(mrn_padded)
  mrn_str.append(mrn_padded)

#checkCoordCongruent(mrn_str, baseDir, modDir)

copyImageOnly(mrn_str, baseDir, modDir, modIndex, df2, outputTrainDir)
#copyLabelOnly(mrn_str, baseDir, labelDir, df_print['MKDIL'], outputTrainLabelDir)

outputJSONName = os.path.join(outputDir, 'dataset.json')
generate_dataset_json(outputJSONName, outputTrainDir, channel_names, labels)
