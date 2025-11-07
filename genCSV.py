import os
import csv
import pydicom



ANONYMIZED_ROOT = r"Z:\DFCI_Anon"

# CSV path where you want to save/update metadata
CSV_PATH = os.path.join(ANONYMIZED_ROOT, "anonymized_metadata.csv")

# Tags you want to log (anonymized + hashed tags)
# Use the same sets from your anonymization process
TAGS_TO_LOG = {
    # Anonymized tags (group, element) tuples
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

HASHED_TAGS = {
    (0x0008, 0x0050), (0x0010, 0x0010), (0x0010, 0x1000),
    (0x0020, 0x0010), (0x0040, 0x0253), (0x0040, 0x1001), (0x0038, 0x0010)
}

ALL_TAGS = TAGS_TO_LOG.union(HASHED_TAGS)

def get_tag_value(ds, tag):
    try:
        elem = ds.get(tag)
        if elem is None:
            return ""
        # For sequences or complex VR, you might want to convert differently if needed
        if elem.VR == "SQ":
            return "<Sequence>"
        # For PersonName, convert to string
        if elem.VR == "PN":
            return str(elem.value)
        # Otherwise, just convert to string
        return str(elem.value)
    except Exception as e:
        return f"<Error: {e}>"

def load_existing_rows(csv_path):
    rows = {}
    if os.path.exists(csv_path):
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["PatientID"], row["SeriesName"])
                rows[key] = row
    return rows

def write_csv(csv_path, rows, fieldnames):
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows.values():
            writer.writerow(row)

def main():
    print(f"Starting to scan anonymized DICOM series under: {ANONYMIZED_ROOT}")
    existing_rows = load_existing_rows(CSV_PATH)
    print(f"Loaded {len(existing_rows)} existing rows from CSV")

    updated_rows = existing_rows.copy()
    total_series = 0
    processed = 0

    # Collect all patient dirs (assumed direct subfolders)
    patient_ids = [d for d in os.listdir(ANONYMIZED_ROOT) if os.path.isdir(os.path.join(ANONYMIZED_ROOT, d))]

    for patient_id in patient_ids:
        patient_path = os.path.join(ANONYMIZED_ROOT, patient_id)
        series_names = [s for s in os.listdir(patient_path) if os.path.isdir(os.path.join(patient_path, s))]
        for series_name in series_names:
            total_series += 1

    print(f"Found {total_series} series total to process.")

    for patient_id in patient_ids:
        patient_path = os.path.join(ANONYMIZED_ROOT, patient_id)
        series_names = [s for s in os.listdir(patient_path) if os.path.isdir(os.path.join(patient_path, s))]
        for series_name in series_names:
            series_path = os.path.join(patient_path, series_name)

            # Skip if row already exists and seems complete
            key = (patient_id, series_name)
            if key in updated_rows:
                processed += 1
                if processed % 100 == 0:
                    print(f"Skipped {processed} series (already in CSV).")
                continue

            # Find a representative DICOM file
            dcm_files = [f for f in os.listdir(series_path) if f.lower().endswith(".dcm")]
            if not dcm_files:
                print(f"Warning: No DICOM files found in {series_path}, skipping.")
                continue

            dcm_path = os.path.join(series_path, dcm_files[0])
            try:
                ds = pydicom.dcmread(dcm_path, stop_before_pixels=True)
            except Exception as e:
                print(f"Failed to read DICOM in {series_path}: {e}")
                continue

            # Prepare row dict
            row = {
                "PatientID": patient_id,
                "SeriesName": series_name,
            }
            for tag in ALL_TAGS:
                row[f"{tag[0]:04X},{tag[1]:04X}"] = get_tag_value(ds, tag)

            updated_rows[key] = row
            processed += 1

            if processed % 100 == 0:
                print(f"Processed {processed}/{total_series} series...")

    # Write all data to CSV
    # Fieldnames: PatientID, SeriesName, then sorted tags as strings
    tag_fieldnames = [f"{tag[0]:04X},{tag[1]:04X}" for tag in sorted(ALL_TAGS)]
    fieldnames = ["PatientID", "SeriesName"] + tag_fieldnames

    write_csv(CSV_PATH, updated_rows, fieldnames)
    print(f"Done! Wrote metadata for {len(updated_rows)} series to {CSV_PATH}")

if __name__ == "__main__":
    main()
