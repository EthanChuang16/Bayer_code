import os
import pydicom
import logging
import concurrent.futures
import time
import threading

#logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

#target SOP Class UID
TARGET_SOP_CLASS_UID = "1.2.840.10008.5.1.4.1.1.4"

#root
ROOT_DIR = r"Z:\DFCI_Anon"

#file list
FILE_LIST_TXT = "dicom_file_list.txt"

#counter
processed_count = 0
processed_lock = threading.Lock()


def gather_dicom_files(root_dir):
    #collect the dicom files
    logging.info(f"Starting file gathering from {root_dir}...")

    dicom_files = []
    count = 0
    start_time = time.time()

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith(".dcm"):
                full_path = os.path.join(dirpath, filename)
                dicom_files.append(full_path)
                count += 1

                if count % 100 == 0:
                    elapsed = time.time() - start_time
                    logging.info(f"Found {count} files so far... ({elapsed:.1f}s elapsed)")

    logging.info(f"Finished gathering files. Total found: {len(dicom_files)}")

    #save list to text file
    with open(FILE_LIST_TXT, "w") as f:
        for path in dicom_files:
            f.write(path + "\n")
    logging.info(f"Saved file list to {FILE_LIST_TXT}")

    return dicom_files


def load_cached_file_list():
    #load the list if it exists
    if os.path.exists(FILE_LIST_TXT):
        logging.info(f"Loading cached file list from {FILE_LIST_TXT}...")
        with open(FILE_LIST_TXT, "r") as f:
            dicom_files = [line.strip() for line in f if line.strip()]
        logging.info(f"Loaded {len(dicom_files)} files from cache.")
        return dicom_files
    return None


def update_sop_class_uid(dicom_path, total_files):
    #update sopclassuid in a dicom file
    global processed_count
    try:
        ds = pydicom.dcmread(dicom_path, force=True)
        ds.SOPClassUID = TARGET_SOP_CLASS_UID
        ds.save_as(dicom_path)
    except Exception as e:
        logging.error(f"Failed to update {dicom_path}: {e}")

    #update progress counter
    with processed_lock:
        processed_count += 1
        if processed_count % 100 == 0 or processed_count == total_files:
            logging.info(f"Processed {processed_count}/{total_files} files...")


def main():
    #load from file array
    dicom_files = load_cached_file_list()
    if dicom_files is None:
        dicom_files = gather_dicom_files(ROOT_DIR)

    total_files = len(dicom_files)
    logging.info(f"Starting SOP Class UID updates on {total_files} files...")

    start_time = time.time()

    #multithreading for speed
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(update_sop_class_uid, f, total_files) for f in dicom_files]
        concurrent.futures.wait(futures)

    elapsed = time.time() - start_time
    logging.info(f"All {total_files} files processed in {elapsed:.1f} seconds.")


if __name__ == "__main__":
    main()
