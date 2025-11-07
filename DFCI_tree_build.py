import os
import shutil
import sys

def count_dcm_files(path):
    return sum(1 for f in os.listdir(path) if f.lower().endswith(".dcm"))

def build_series_tree(dfci_root, anon_root):
    if not os.path.exists(dfci_root):
        print(f"Source directory does not exist: {dfci_root}")
        return
    if not os.path.exists(anon_root):
        os.makedirs(anon_root)

    for patient_id in os.listdir(dfci_root):
        patient_path = os.path.join(dfci_root, patient_id)
        if not os.path.isdir(patient_path):
            continue

        for exam_folder in os.listdir(patient_path):
            exam_path = os.path.join(patient_path, exam_folder)
            if not os.path.isdir(exam_path):
                continue

            mr_path = os.path.join(exam_path, "MR")
            if not os.path.isdir(mr_path):
                continue

            for series_folder in os.listdir(mr_path):
                series_path = os.path.join(mr_path, series_folder)
                if not os.path.isdir(series_path):
                    continue

                dest_series_path = os.path.join(anon_root, patient_id, series_folder)

                #Check if destination exists and is complete
                if os.path.exists(dest_series_path):
                    src_count = count_dcm_files(series_path)
                    dest_count = count_dcm_files(dest_series_path)

                    if dest_count >= src_count:
                        print(f"Skipping {series_path} (already copied)")
                        continue
                    else:
                        print(f"Incomplete copy detected for {dest_series_path}, re-copying")
                        shutil.rmtree(dest_series_path)  

                #Ensure patient folder exists
                os.makedirs(os.path.dirname(dest_series_path), exist_ok=True)

                shutil.copytree(series_path, dest_series_path)
                print(f"Copied: {series_path} -> {dest_series_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python DFCI_tree_build.py <DFCI_root> <DFCI_Anon_root>")
        sys.exit(1)

    dfci_root = sys.argv[1]
    dfci_anon_root = sys.argv[2]

    build_series_tree(dfci_root, dfci_anon_root)
