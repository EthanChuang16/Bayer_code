import os
import sys
import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt

def write_dicom_to_nifti(dicom_dir, output_path):
    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(dicom_dir)
    reader.SetFileNames(dicom_names)
    image = reader.Execute()
    sitk.WriteImage(image, output_path)
    print(f"Saved NIfTI to: {output_path}")
    return image

def read_image(path):
    reader = sitk.ImageFileReader()
    reader.SetFileName(path)
    image = reader.Execute()
    array = sitk.GetArrayFromImage(image)
    return image, array

def plot_image(image, output_png_path, hi_bval=5):
    array = sitk.GetArrayFromImage(image)
    nz = min(array.shape[0], 25)
    fig, ax = plt.subplots(5, 5, figsize=(10, 10))
    ax = ax.flatten()

    if hi_bval == 5:
        vmin, vmax = -250, 1500
    else:
        vmin = np.percentile(array, 1)
        vmax = np.percentile(array, 99)

    for i in range(nz):
        ax[i].axis('off')
        ax[i].imshow(array[i, :, :], cmap='gray', vmin=vmin, vmax=vmax)

    plt.savefig(output_png_path)
    plt.close(fig)
    print(f"Saved PNG to: {output_png_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python DICOM_to_NIFTI_and_PNG.py <DICOM_series_path>")
        sys.exit(1)

    dicom_dir = sys.argv[1]
    if not os.path.isdir(dicom_dir):
        print(f"Invalid directory: {dicom_dir}")
        sys.exit(1)

    # Extract metadata from path
    path_parts = os.path.normpath(dicom_dir).split(os.sep)
    if len(path_parts) < 2:
        print("Unable to extract PatientID and Series name from path.")
        sys.exit(1)

    patient_id = path_parts[-2]
    series_name = path_parts[-1]
    base_dir = os.path.dirname(os.path.dirname(dicom_dir))  # Go up two levels

    # Output paths
    nifti_path = os.path.join(os.path.dirname(dicom_dir), f"{series_name}.nii.gz")
    fig_dir = os.path.join(base_dir, "DFCI_Figs")
    os.makedirs(fig_dir, exist_ok=True)
    png_filename = f"{patient_id}___{series_name}.png"
    png_path = os.path.join(fig_dir, png_filename)

    # Convert and save
    image = write_dicom_to_nifti(dicom_dir, nifti_path)
    plot_image(image, png_path, hi_bval=5)

    print("Done.")

if __name__ == "__main__":
    main()
