import os
import pydicom

# Replace this with the path to the series folder you want to inspect
SERIES_DIR = "Z:/DFCI_Anon/97442689/2__AX_T2_ant_sat"

def print_dicom_tags(dcm_path):
    try:
        ds = pydicom.dcmread(dcm_path, stop_before_pixels=True, force=True)
        print(f"\n[INFO] DICOM file: {dcm_path}\n")
        for elem in ds:
            print(f"{elem.name}: {elem.value}")
    except Exception as e:
        print(f"[ERROR] Failed to read DICOM file: {e}")

def main():
    dcm_files = [f for f in os.listdir(SERIES_DIR) if f.lower().endswith(".dcm")]
    if not dcm_files:
        print("[ERROR] No DICOM files found in this folder.")
        return

    first_dcm = os.path.join(SERIES_DIR, dcm_files[0])
    print_dicom_tags(first_dcm)

if __name__ == "__main__":
    main()
