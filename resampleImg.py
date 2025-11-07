import os
import DILFunctions
import pandas as pd
import SimpleITK as sitk
baseDir = 'D:\\MGHMRI_Proc'

imgDir = ['ADC2_crop','DWI_Extract2_Info_Img_crop']#, 'DWI_Extract2_Info_Img_crop_OriginVerified']
templateDir = 'T2_crop'

suffix = '_resample'

os.chdir(baseDir)

df = pd.read_csv('D:\\MGHMRI_Proc\\adt_test_mod052725_poistMerge.csv')
df2 = df[pd.isna(df['Exclude'])]
#df3 = df2[pd.isna(df2['Reg'])]
df3 = df2[df2['PatientID'] == 2031639]

newSize = (128, 128, 20)


for cti, i in enumerate(imgDir):
  resampleDir = i + suffix
  if not (os.path.isdir(resampleDir)):
    os.mkdir(resampleDir)
  else:
    print('Resample directory already present')

  resampleDirFig = i + suffix + '_Fig'
  if not (os.path.isdir(resampleDirFig)):
    os.mkdir(resampleDirFig)
  else:
    print('resampleDirFig already present')

  for index, row in df3.iterrows():
    mrn = str(row['MRN'])
    mrn_padded = mrn.zfill(7)
    fname = mrn_padded + '.nii.gz'
    template_fullimgname = os.path.join(baseDir, templateDir, fname)
    figName = os.path.join(resampleDirFig, fname.split('.')[0] + '.png')
    if  (os.path.isfile(figName)):

      template_imgsitk, template_img = DILFunctions.readImageFcn(template_fullimgname)

      newSpacing = (0.7031, 0.7031, template_imgsitk.GetSpacing()[2])

      imgsitk, img = DILFunctions.readImageFcn(i + '\\' + fname)

      resampleFilterOut = sitk.ResampleImageFilter()
      resampleFilterOut.SetSize(template_imgsitk.GetSize())
      resampleFilterOut.SetOutputSpacing(template_imgsitk.GetSpacing())
      resampleFilterOut.SetOutputOrigin(template_imgsitk.GetOrigin())
      resampleFilterOut.SetOutputDirection(template_imgsitk.GetDirection())
      resampled_sitk = resampleFilterOut.Execute(imgsitk)

      outputImageName = os.path.join(resampleDir, fname)
      sitk.WriteImage(resampled_sitk, outputImageName)
      print('Input image origin: ', imgsitk.GetOrigin(), ' Template image origin: ', template_imgsitk.GetOrigin(), ' Output image origin: ', resampled_sitk.GetOrigin())
      print('Input image spacing: ', imgsitk.GetSpacing(), ' Template image spacing: ', template_imgsitk.GetSpacing(), ' Output image spacing: ', resampled_sitk.GetSpacing())
      print('Wrote: ', outputImageName, ' based on template: ', template_fullimgname)
      fig_resampleimgsitk, fig_resampleimg = DILFunctions.readImageFcn(outputImageName)

      DILFunctions.plotimgOnly(fig_resampleimgsitk, figName, 3)
