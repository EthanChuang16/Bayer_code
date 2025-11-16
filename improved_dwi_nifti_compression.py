import os
import numpy as np
import pandas as pd
import SimpleITK as sitk
import traceback
import ast

# -------------------------------------------------
# Helper: Read series of DICOM slices into NumPy + SITK image
# -------------------------------------------------
def load_dicom_series(series_path):
    """Load a folder of DICOM slices (sorted) → SITK image + NumPy array."""
    dicom_files = [
        os.path.join(series_path, f)
        for f in os.listdir(series_path)
        if f.lower().endswith(".dcm")
    ]

    if not dicom_files:
        raise RuntimeError(f"No DICOM files found in: {series_path}")

    # Read metadata, sort by InstanceNumber
    slices = []
    for f in dicom_files:
        dcm = sitk.ReadImage(f)
        inst = int(sitk.ReadImage(f).GetMetaData("0020|0013"))  # InstanceNumber
        slices.append((inst, f))

    slices.sort(key=lambda x: x[0])
    sorted_files = [f for _, f in slices]

    reader = sitk.ImageSeriesReader()
    reader.SetFileNames(sorted_files)
    sitk_img = reader.Execute()
    np_img = sitk.GetArrayFromImage(sitk_img)

    return sitk_img, np_img


# -------------------------------------------------
# MAIN SCRIPT
# -------------------------------------------------
csv_path = os.path.join('D:\\MGHMRI', 'DWI_ZInc_Pass2_mod.csv')
df = pd.read_csv(csv_path)

baseDir = 'D:\\MGHMRI_Proc'
dicomRoot = os.path.join(baseDir, 'DWI2')  # existing structure: base/Patient/Series/*.dcm

print("Starting DICOM → NIfTI + High-b extraction...")

for _, row in df.iterrows():

    mrn = str(row['PatientID']).zfill(7)
    seriesNumber = row.get('SeriesNumber')

    if pd.isna(row['SlicesPerVolume']):
        continue

    try:
        seriesNumber = int(seriesNumber)
        series_path = os.path.join(dicomRoot, mrn, str(seriesNumber))

        if not os.path.isdir(series_path):
            print(f"Missing DICOM directory for patient {mrn}, series {seriesNumber}")
            continue

        print(f"Processing MRN {mrn} | Series {seriesNumber}")

        # Load DICOM stack
        sitk_img, img_np = load_dicom_series(series_path)
        img_shape = img_np.shape  # (numSlices, H, W)

        slicesPerVolume = int(row['SlicesPerVolume'])
        numVolumes = int(row['NumVolumes'])
        numIncreasing = int(row['Increasing'])
        numDecreasing = int(row['Decreasing'])

        bval_list = ast.literal_eval(row['Bvals'])
        GradX_list = ast.literal_eval(row['GradX'])
        GradY_list = ast.literal_eval(row['GradY'])
        GradZ_list = ast.literal_eval(row['GradZ'])

        # -------------------------------------------------
        # WRITE ORIGINAL NIFTI
        # -------------------------------------------------
        nii_out = os.path.join(series_path, f"{mrn}_{seriesNumber}.nii.gz")
        sitk.WriteImage(sitk_img, nii_out)

        # -------------------------------------------------
        # RESHAPE TO (numVolumes, slicesPerVolume, H, W)
        # -------------------------------------------------
        img_reshaped = img_np.reshape(numVolumes, slicesPerVolume, img_shape[1], img_shape[2])

        # -------------------------------------------------
        # EXTRACT HIGH B-VALUE
        # -------------------------------------------------
        bmax = max(bval_list)
        bmax_idx = [i for i, v in enumerate(bval_list) if v == bmax]

        if len(bmax_idx) == 1:
            highb = img_reshaped[bmax_idx[0]]
        elif len(bmax_idx) == 12:
            highb = np.mean(img_reshaped[bmax_idx, :, :, :], axis=0)
        else:
            highb = img_reshaped[bmax_idx[0]]

        # Flip if decreasing > increasing
        if numVolumes > 1 and numDecreasing > numIncreasing:
            highb = np.flip(highb, axis=0)

        # Convert to SITK and save
        highb_img = sitk.GetImageFromArray(highb)
        highb_img.SetOrigin(sitk_img.GetOrigin())
        highb_img.SetDirection(sitk_img.GetDirection())
        highb_img.SetSpacing(sitk_img.GetSpacing())

        out_highb = os.path.join(series_path, f"{mrn}_{seriesNumber}_highb.nii.gz")
        sitk.WriteImage(highb_img, out_highb)

    except Exception as e:
        print(f"ERROR on MRN {mrn}: {e}")
        traceback.print_exc()
        continue

print("Done.")
