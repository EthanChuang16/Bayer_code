import os
import csv
from collections import Counter

#paths
os.chdir(r'Z:\MRI_Report')  #same directory where filteredMRI.csv is
input_csv = "filteredMRI.csv"
output_txt = "repeats.txt"

#read PMRN values from CSV
pmrn_counts = Counter()
with open(input_csv, "r", newline="") as infile:
    reader = csv.reader(infile)
    header = next(reader)
    pmrn_index = header.index("PMRN")  #find column dynamically

    for row in reader:
        pmrn = row[pmrn_index].strip()
        if pmrn:  # skip empty values
            pmrn_counts[pmrn] += 1

#find repeats
repeats = {pmrn: count for pmrn, count in pmrn_counts.items() if count > 1}

#write repeats to a text file
with open(output_txt, "w") as outfile:
    outfile.write("PMRN\tCount\n")
    for pmrn, count in repeats.items():
        outfile.write(f"{pmrn}\t{count}\n")

print(f"Found {len(repeats)} repeated PMRN(s). Results written to {output_txt}")
