import os
import sys
import pydicom
import nibabel as nib
import numpy as np

def dicom_series_to_nifti(series_path):
    # Get all .dcm files in the folder
    dicom_files = [os.path.join(series_path, f) 
                   for f in os.listdir(series_path) 
                   if f.lower().endswith(".dcm")]

    if not dicom_files:
        print(f"No DICOM files found in {series_path}")
        return

    # Load all slices
    slices = [pydicom.dcmread(f) for f in dicom_files]
    slices.sort(key=lambda x: float(x.InstanceNumber))

    # Build a 3D numpy volume
    volume = np.stack([s.pixel_array for s in slices])

    # Build affine from DICOM orientation values
    first = slices[0]
    orientation = np.array(first.ImageOrientationPatient).reshape(2, 3)
    spacing = np.array([float(first.PixelSpacing[0]), 
                        float(first.PixelSpacing[1]), 
                        float(first.SliceThickness)])
    direction = np.vstack((orientation,
                           np.cross(orientation[0], orientation[1])))
    affine = np.eye(4)
    affine[:3, :3] = direction * spacing
    affine[:3, 3] = np.array(first.ImagePositionPatient)

    # Save NIfTI file
    output_path = os.path.join(series_path, "series.nii.gz")
    nib.save(nib.Nifti1Image(volume, affine), output_path)

    print(f"Saved NIfTI: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_adc_t2.py <path_to_series_folder>")
        sys.exit(1)

    dicom_series_to_nifti(sys.argv[1])
