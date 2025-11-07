import DILFunctions
import os, subprocess
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
from skimage import filters
import pydicom
from pydicom import dcmread
import pandas as pd
from pydicom.tag import Tag
import traceback

#Exception: 2837626: String index outof range.
#Exception: 3145176: String index outof range.

def count_increasing_decreasing(lst):
  increasing = sum(1 for x, y in zip(lst, lst[1:]) if x < y)
  decreasing = sum(1 for x, y in zip(lst, lst[1:]) if x > y)
  return increasing, decreasing

from pathlib import Path
import pandas as pd
from pydicom import dcmread
from pydicom.tag import Tag

def extract_mri_metadata(df, sourceDir):
    def count_increasing_decreasing(values):
        inc = sum(1 for i in range(1, len(values)) if values[i] > values[i - 1])
        dec = sum(1 for i in range(1, len(values)) if values[i] < values[i - 1])
        return inc, dec

    def append_entry(patient_id, series_num, model, series, manufacturer, nslices, inc_ct, dec_ct, bvals, ndirection, gradx, grady, gradz, slices_per_volume, n_volumes):
        return {
            'PatientID': patient_id,
            'SeriesNumber': series_num,
            'Model': model,
            'Series': series,
            'Manufacturer': manufacturer,
            'NumSlices': nslices,
            #'ZPositions': z_positions,
            'Increasing': inc_ct,
            'Decreasing': dec_ct,
            'Bvals': bvals,
            'NumDirection': ndirection,
            'GradX': gradx,
            'GradY': grady,
            'GradZ': gradz,
            'SlicesPerVolume': slices_per_volume,
            'NumVolumes': n_volumes
        }

    results = []

    for _, row in df.iterrows():
        mrn = str(row['PatientID']).zfill(7)
        seriesNumber = row.get('DWIMatches_filter_series2')
        exclude = row.get('Exclude')

        if (exclude == 1):
        #if pd.isna(seriesNumber):
            print(f"Patient ID {mrn} is excluded.")
            results.append(append_entry(mrn, seriesNumber, None, None, None, None, None, None, None, None, None, None, None, None, None))
            continue

        seriesNumber = int(seriesNumber)
        print(f"Patient ID: {mrn} | Series number: {seriesNumber}")

        try:
            mrn_dir = Path(sourceDir) / mrn
            subdir1 = next(mrn_dir.iterdir())  # First subdir (e.g., date or scan folder)
            series_path = mrn_dir / subdir1 / 'MR'

            # Match series folder
            matches = [s for s in os.listdir(series_path) if str(s).startswith(f"{seriesNumber}_")]
            if not matches:
                print("  No matching series directory.")
                results.append(append_entry(mrn, seriesNumber, None, None, None, None, None, None, None, None, None, None, None, None, None))
                continue

            series_dir = series_path / matches[0]
            dcmfiles = sorted([f for f in os.listdir(series_dir) if f.endswith('.dcm')])
            print(f"  Number of DICOM files: {len(dcmfiles)}")

            if not dcmfiles:
                print("  No DICOM files found.")
                results.append(append_entry(mrn, seriesNumber, None, None, None, None, None, None, None, None, None, None, None, None, None))
                continue

            # Read DICOMs
            ds_slice = [dcmread(series_dir / f) for f in dcmfiles]
            ds0 = ds_slice[0]

            model = getattr(ds0, "ManufacturerModelName", None)
            series = getattr(ds0, "SeriesDescription", None)
            manufacturer = getattr(ds0, "Manufacturer", None)

            z_positions = [float(ds.ImagePositionPatient[2]) for ds in ds_slice if hasattr(ds, "ImagePositionPatient")]
            nslices = len(z_positions)
            inc_ct, dec_ct = count_increasing_decreasing(z_positions)

            # Step 1: Find how many unique slices there are
            unique_z = list(dict.fromkeys(z_positions))  # preserves order
            slices_per_volume = len(unique_z)

            # Step 2: Count how many times the pattern repeats
            total_slices = len(z_positions)
            n_volumes = total_slices // slices_per_volume

            # Step 3: Assign volume indices
            volume_indices = [i // slices_per_volume for i in range(total_slices)]

            # Choose correct private tag
            private_tag = Tag(0x0043, 0x1039) if manufacturer == 'GE MEDICAL SYSTEMS' else Tag(0x0019, 0x100c)
            bvals_unprocessed = [ds.get(private_tag).value if ds.get(private_tag) else ""
                for ds in ds_slice]
            bvals = [b[0] % 1000000000 for b in bvals_unprocessed] if manufacturer == 'GE MEDICAL SYSTEMS' else bvals_unprocessed
            #print('Bvals: ', bvals)
            bvals_volume = list(np.array(bvals)[np.arange(n_volumes) * slices_per_volume])
            print('Bvals volume: ', bvals_volume)
            if manufacturer == 'GE MEDICAL SYSTEMS':
              private_tag = Tag(0x0019, 0x10e0)
              ndirection = [ds.get(private_tag).value if ds.get(private_tag) else ""
                for ds in ds_slice]
              ndirection = list(set(ndirection))

              private_tag = Tag(0x0019, 0x10bb)
              gradx = [ds.get(private_tag).value if ds.get(private_tag) else ""
                for ds in ds_slice]
              gradx_volume = list(np.array(gradx)[np.arange(n_volumes) * slices_per_volume])

              private_tag = Tag(0x0019, 0x10bc)
              grady = [ds.get(private_tag).value if ds.get(private_tag) else ""
                for ds in ds_slice]
              grady_volume = list(np.array(grady)[np.arange(n_volumes) * slices_per_volume])

              private_tag = Tag(0x0019, 0x10bd)
              gradz = [ds.get(private_tag).value if ds.get(private_tag) else ""
                for ds in ds_slice]
              gradz_volume = list(np.array(gradz)[np.arange(n_volumes) * slices_per_volume])
            else:
              ndirection = None

              private_tag = Tag(0x0019, 0x100e)
              grad_coord = [ds.get(private_tag).value if ds.get(private_tag) else None
                for ds in ds_slice]
              grad_coord_volume = list(np.array(grad_coord)[np.arange(n_volumes) * slices_per_volume])
              gradx_volume = [arr[0] for arr in grad_coord_volume if arr is not None]
              grady_volume = [arr[1] for arr in grad_coord_volume if arr is not None]
              gradz_volume = [arr[2] for arr in grad_coord_volume if arr is not None]

            #Only one
            #seriesID = [ds.SeriesInstanceUID for ds in ds_slice]
            #combined = list(zip(bvals, z_positions, ndirection, gradx, grady, gradz))

            results.append(append_entry(mrn, seriesNumber, model, series, manufacturer, nslices, inc_ct, dec_ct, bvals_volume, ndirection, gradx_volume, grady_volume, gradz_volume, slices_per_volume, n_volumes))

        except Exception as e:
            print(f"  Error processing MRN {mrn}: {e}")
            traceback.print_exc()
            results.append(append_entry(mrn, seriesNumber, None, None, None, None, None, None, None, None, None, None, None, None, None))

    return pd.DataFrame(results)

sourceDir = 'D:\\MGHMRI'

#df = pd.read_csv(os.path.join(sourceDir, 'subdirectories_ADC_mod_Edited_Pass1.csv'))
df = pd.read_csv(os.path.join(sourceDir, 'subdirectories_ADC_mod_Edited_Pass2.csv'))
#checklist = [2837626, 3145176] # Two series 500 labeled. Got rid of one.
#checklist = [3145176]
#df = df[df['PatientID'].isin(checklist)]
#df = df[df['PatientID'] == 4145654]
outname = os.path.join(sourceDir, 'DWI_ZInc_Pass2.csv')
final_df = extract_mri_metadata(df, sourceDir)

final_df.to_csv(outname)
  # 27; #42, #43, 44

