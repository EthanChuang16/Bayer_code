import os
import csv


os.chdir(r"Z:\MRI_Report")


input_file = "midas_combined.csv"
output_file = "midas_hashmap.txt"

print(f"Creating text-based hashmap from {input_file}...")

if not os.path.exists(input_file):
    raise FileNotFoundError(f"Cannot find {input_file} in current directory.")

midas_map = {}

with open(input_file, "r", newline="", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    fieldnames = [name.strip().lower() for name in reader.fieldnames]

    mrn_col = next((name for name in fieldnames if "mrn" in name), None)
    acc_col = next((name for name in fieldnames if "accession" in name), None)

    if not mrn_col or not acc_col:
        raise ValueError("CSV missing MRN or AccessionNumber columns.")

    for row in reader:
        row_lower = {k.lower(): v.strip() for k, v in row.items()}
        mrn = row_lower.get(mrn_col)
        accession = row_lower.get(acc_col)

        if not mrn or not accession:
            continue

        
        if mrn in midas_map:
            if accession not in midas_map[mrn]:
                midas_map[mrn].append(accession)
        else:
            midas_map[mrn] = [accession]


with open(output_file, "w", encoding="utf-8") as outfile:
    for mrn, acc_list in midas_map.items():
        if len(acc_list) == 1:
            outfile.write(f"{mrn} -> {acc_list[0]}\n")
        else:
            outfile.write(f"{mrn} -> {acc_list}\n")

print(f"\n Hashmap text file created: {output_file}")
print(f"Total unique MRNs written: {len(midas_map)}")


print("\nSample entries:")
for i, (mrn, acc) in enumerate(midas_map.items()):
    print(f"{mrn} -> {acc}")
    if i == 4:
        break
