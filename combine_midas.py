import os
import csv

os.chdir(r"Z:\MRI_Report")


input_files = ["MIDAS_Submit0225.csv", "MIDAS_Submit102324.csv"]
output_file = "midas_combined.csv"

print(f"Combining MIDAS files: {input_files}")

seen_pairs = set()
count_written = 0

with open(output_file, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=["MRN", "AccessionNumber"])
    writer.writeheader()

    for file in input_files:
        if not os.path.exists(file):
            print(f"Skipping missing file: {file}")
            continue

        with open(file, "r", newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            # Normalize column names
            fieldnames = [name.strip().lower() for name in reader.fieldnames]
            mrn_col = next((name for name in fieldnames if "mrn" in name), None)
            acc_col = next((name for name in fieldnames if "accession" in name), None)

            if not mrn_col or not acc_col:
                print(f"Skipping {file} — missing MRN or Accession column.")
                continue

            print(f"Processing {file}...")

            for row in reader:
                row_lower = {k.lower(): v.strip() for k, v in row.items()}
                mrn = row_lower.get(mrn_col, "")
                accession = row_lower.get(acc_col, "")

                if not mrn or not accession:
                    continue

                #Pad MRNs to 8 digits
                mrn = mrn.zfill(8)

                pair = (mrn, accession)
                if pair not in seen_pairs:
                    writer.writerow({"MRN": mrn, "AccessionNumber": accession})
                    seen_pairs.add(pair)
                    count_written += 1

print(f"\n Combined file created: {output_file}")
print(f"Total unique MRN–Accession pairs written: {count_written}")
