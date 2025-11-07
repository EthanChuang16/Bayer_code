import os
import sys
import pydicom
from pydicom.uid import UID
from pydicom.valuerep import PersonName
import hashlib
import shutil
import csv
from datetime import datetime
import threading

#global lock 
csv_lock = threading.Lock()

#new helper to check if already processed
def is_series_already_processed(csv_path, patient_id, series_name):
    if not os.path.exists(csv_path):
        return False
    with open(csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get("PatientID") == patient_id and row.get("SeriesName") == series_name:
                return True
    return False


#Helper functions 

#for uid fields
def transform_uid_sha256(original_uid: str) -> str:
    sha256 = hashlib.sha256(original_uid.encode('utf-8')).digest()
    hashed_int = int.from_bytes(sha256, byteorder='big')
    base10_str = str(hashed_int)
    uid = f"2.25.{base10_str}"
    if len(uid) > 64:
        uid = uid[:64].rstrip('.')
    return UID(uid)

#for specified fields
def hash_string(input_str: str, length: int = 16) -> str:
    sha256_hash = hashlib.sha256(input_str.encode('utf-8')).hexdigest()
    return sha256_hash[:length]

#helper to clear values safely based on VR
def clear_element_value(elem):
    try:
        if elem.VR in ("US", "UL", "SS", "SL", "IS", "DS"):
            elem.value = 0
        elif elem.VR == "PN":
            elem.value = PersonName("")
        elif elem.VR in ("DA", "DT", "TM"):
            elem.value = ""
        elif elem.VR == "SQ":
            elem.value = []
        else:
            elem.value = ""
    except Exception:
        elem.value = None

#helper to create and update csv file
def update_or_create_csv(csv_path, patient_id, series_name, fields_dict):
    row_key = (patient_id, series_name)
    new_row = {
        "PatientID": patient_id,
        "SeriesName": series_name,
        **fields_dict
    }
    #thread safe writing
    with csv_lock:

        existing_rows = []
        fieldnames = set(new_row.keys())

        if os.path.exists(csv_path):
            with open(csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                existing_rows = list(reader)
                for row in existing_rows:
                    fieldnames.update(row.keys())

        #explicit order 
        fieldnames = list(fieldnames)  # Ensure consistent ordering
        other_fields = [f for f in fieldnames if f not in ("PatientID", "SeriesName")]
        fieldnames = ["PatientID", "SeriesName"] + sorted(other_fields)

        updated = False
        for row in existing_rows:
            if row["PatientID"] == patient_id and row["SeriesName"] == series_name:
                row.update(new_row)
                updated = True
                break

        if not updated:
            existing_rows.append(new_row)

        # Write updated CSV with full header
        with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_rows)

#fields to anonymize
tags_to_mask = {
    (0x0010, 0x0030), (0x0010, 0x0032), (0x0010, 0x0040),
    (0x0010, 0x1001), (0x0010, 0x1040), (0x0010, 0x2154), (0x0010, 0x4000),
    (0x0008, 0x0090), (0x0008, 0x1048), (0x0008, 0x1060),
    (0x0008, 0x1010), (0x0008, 0x1040), (0x0008, 0x1070),
    (0x0018, 0x1000), (0x0008, 0x0020), (0x0008, 0x0030),
    (0x0008, 0x0021), (0x0008, 0x0031), (0x0008, 0x0022), (0x0008, 0x0032),
    (0x0008, 0x0023), (0x0008, 0x0033), (0x0040, 0xA124),
    (0x0008, 0x0080), (0x0010, 0x1010), (0x0010, 0x1020),
    (0x0010, 0x1030), (0x0008, 0x0012), (0x0008, 0x0013),
    (0x0008, 0x0016), (0x0008, 0x0018), (0x0008, 0x0081),
    (0x0008, 0x1030), (0x0010, 0x2150), (0x0010, 0x2160),
    (0x0010, 0x21A0), (0x0010, 0x21C0), (0x0010, 0x21F0),
    (0x0012, 0x0020), (0x0012, 0x0031), (0x0012, 0x0042),
    (0x0018, 0x0015), (0x0032, 0x1032), (0x0002, 0x0003),
    (0x0002, 0x0012), (0x0020, 0x000D), (0x0020, 0x000E),
    (0x0020, 0x0052), (0x0040, 0x0242), (0x0040, 0x0243),
    (0x0040, 0x0244), (0x0040, 0x0245), (0x0040, 0x0009),
    (0x0400, 0x0561), (0x0400, 0x0562), (0x0400, 0x0563),
    (0x0400, 0x0564), (0x0400, 0x0565), (0x2110, 0x0030),
    (0x0008, 0x002A), (0x0040, 0x0275), (0x0040, 0x2016),
    (0x0040, 0x2017), (0x0008, 0x103E), (0x0008, 0x1110),
    (0x0012, 0x0082), (0x0010, 0x0021), (0x0040, 0xA170),
    (0x0008, 0x0100), (0x0008, 0x0102), (0x0008, 0x0104),
    (0x0012, 0x0062), (0x0019, 0x109D), (0x0043, 0x1061),
    (0x0008, 0x1250), (0x0008, 0x1150), (0x0008, 0x1160),
    (0x0029, 0x1009), (0x0029, 0x1019),
}


#fields to hash

hash_string_tags = {
    (0x0008, 0x0050), (0x0010, 0x0010), (0x0010, 0x1000),
    (0x0020, 0x0010), (0x0040, 0x0253), (0x0040, 0x1001), (0x0038, 0x0010)
}

#anonymize function
def anonymize_element(ds, elem, tag_tuple, new_patient_id):
    if elem.VR == "SQ":
        for item in elem.value:
            for sub_elem in item.iterall():
                anonymize_element(item, sub_elem, (sub_elem.tag.group, sub_elem.tag.element), new_patient_id)
    elif tag_tuple in hash_string_tags:
        if tag_tuple == (0x0010, 0x0010):
            elem.value = PersonName(hash_string(str(elem.value)))
        else:
            elem.value = hash_string(str(elem.value))
    elif tag_tuple == (0x0010, 0x0020):  # Patient ID
        elem.value = new_patient_id
    elif tag_tuple in tags_to_mask:
        if "UID" in elem.name.upper():
            elem.value = transform_uid_sha256(str(elem.value))
        else:
            clear_element_value(elem)

#main script 

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python DICOM_Anon.py <original_series_path>")
        sys.exit(1)

    series_path = sys.argv[1]
    if not os.path.exists(series_path):
        print(f"Provided path does not exist: {series_path}")
        sys.exit(1)

    #skip if folder has no dcm files in it 
    if not any(f.lower().endswith('.dcm') for f in os.listdir(series_path)):
        print(f"[SKIP] No DICOM files found in: {series_path}")
        sys.exit(0)
    #get new paitent ID from path
    path_parts = os.path.normpath(series_path).split(os.sep)
    if len(path_parts) < 2:
        print("Could not determine patient ID from path.")
        sys.exit(1)
    new_patient_id = path_parts[-2]

    print("Running anonymization...")

    #printed = False
    series_name = os.path.basename(series_path)
    #ensure its placed at same level as patient ids
    patient_dir = os.path.dirname(os.path.dirname(series_path))
    csv_path = os.path.join(patient_dir, "anonymized_metadata.csv")

    #skip processesing if already done
    if is_series_already_processed(csv_path, new_patient_id, series_name):
        print(f"[SKIPPED] {new_patient_id}/{series_name} already processed.")
        sys.exit(0)

    print(f"[STARTING] Anonymizing {new_patient_id}/{series_name}")

    printed = False
    for filename in os.listdir(series_path):
        filepath = os.path.join(series_path, filename)
        if not filename.lower().endswith(".dcm"):
            continue
        try:
            ds = pydicom.dcmread(filepath)

            # Apply anonymization
            for elem in ds.iterall():
                tag_tuple = (elem.tag.group, elem.tag.element)
                anonymize_element(ds, elem, tag_tuple, new_patient_id)

            # Save modified file
            ds.save_as(filepath)

            # Only collect and save field info once
            if not printed:
                field_values = {}
                for elem in ds.iterall():
                    if elem.VR not in ("OB", "OW", "UN", "OF", "UT") and elem.tag != (0x7fe0, 0x0010):
                        tag_tuple = (elem.tag.group, elem.tag.element)
                        if tag_tuple in tags_to_mask or tag_tuple in hash_string_tags or tag_tuple == (0x0010, 0x0020):
                            field_values[elem.name] = str(elem.value)

                update_or_create_csv(csv_path, new_patient_id, series_name, field_values)
                print(f"Metadata written to CSV: {csv_path}")
                printed = True

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print("Anonymization complete.")
