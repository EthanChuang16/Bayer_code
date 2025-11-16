import os
import shutil

# Base path where patient folders are located
BASE_PATH = "/mnt/gcs_mount/250_bucket"

# Destination directory for renamed NIfTI files
IMAGES_DIR = os.path.join(BASE_PATH, "Images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Map series keywords to suffixes
SERIES_SUFFIX = {
    "dwi": "_000",
    "adc": "_001",
    "t2": "_002"
}

def main():
    # Loop over all patients
    for patient in sorted(os.listdir(BASE_PATH)):
        patient_path = os.path.join(BASE_PATH, patient)
        if not os.path.isdir(patient_path):
            continue

        # Loop over series folders
        for series_folder in os.listdir(patient_path):
            series_path = os.path.join(patient_path, series_folder)
            if not os.path.isdir(series_path):
                continue

            # Check for NIfTI files in the series folder
            nifti_files = [f for f in os.listdir(series_path) if f.endswith(".nii") or f.endswith(".nii.gz")]
            if not nifti_files:
                continue  # no NIfTI found in this series folder

            # Determine series type based on folder name
            series_type = None
            folder_lower = series_folder.lower()
            for key in SERIES_SUFFIX:
                if key in folder_lower:
                    series_type = key
                    break

            if series_type is None:
                print(f"[WARN] Could not determine series type for {series_folder} in patient {patient}")
                continue

            # Rename and copy each NIfTI file
            for nifti_file in nifti_files:
                src_file = os.path.join(series_path, nifti_file)
                dst_file = os.path.join(IMAGES_DIR, f"{patient}{SERIES_SUFFIX[series_type]}.nii.gz")
                
                # Copy the file
                shutil.copy2(src_file, dst_file)
                print(f"Copied {src_file} -> {dst_file}")

if __name__ == "__main__":
    main()
