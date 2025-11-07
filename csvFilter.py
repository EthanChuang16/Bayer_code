import os
import csv

# Paths
os.chdir(r'Z:\MRI_Report')  #same directory where CSV and hashmap.txt exist
input_csv = "testMRI.csv"
hashmap_file = "hashmap.txt"
output_csv = "filteredMRI.csv"

#read hashmap.txt into a set of valid PMRN values for fast look up
valid_pmrs = set()
with open(hashmap_file, "r") as hm:
    for line in hm:
        key = line.strip()
        if key:  #skip empty lines
            valid_pmrs.add(key)

print(f"Loaded {len(valid_pmrs)} valid PMRN keys from {hashmap_file}")

#filter CSV rows
with open(input_csv, "r", newline="") as infile, \
     open(output_csv, "w", newline="") as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    header = next(reader)  #keep header
    writer.writerow(header)

    pmrn_index = header.index("PMRN")  #get PMRN column index dynamically

    kept_rows = 0
    removed_rows = 0

    for row in reader:
        if row[pmrn_index] in valid_pmrs:
            writer.writerow(row)
            kept_rows += 1
        else:
            removed_rows += 1

print(f"Filtered CSV written to {output_csv}")
print(f"Kept {kept_rows} rows, removed {removed_rows} rows")
