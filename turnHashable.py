# Define input and output file paths
input_file = "Z:\PythonScripts\ScrambledKey"
output_file = "hashmap.txt"

#init an empty dictionary
hashmap = {}

#read the input file and build the hashmap
with open(input_file, "r") as f:
    for line in f:
        line = line.strip()
        if "->" in line:
            key, value = line.split("->")
            key = key.strip()
            value = value.strip()
            hashmap[key] = value

#write the hashmap to a new file
with open(output_file, "w") as f:
    for key, value in hashmap.items():
        f.write(f"{key}: {value}\n")

print(f"Hashmap saved to {output_file}")
