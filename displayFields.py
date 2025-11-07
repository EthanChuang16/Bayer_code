import pydicom

def dicom_to_txt(dicom_path, output_txt):
    #load dicom file
    ds = pydicom.dcmread(dicom_path)

    with open(output_txt, "w", encoding="utf-8") as f:
        for elem in ds:
            #skip private tags
            if elem.tag.is_private:
                continue

            # Write Tag Name = Value
            f.write(f"{elem.keyword or elem.name}: {elem.value}\n")

if __name__ == "__main__":
    dicom_file = r"Z:\DFCI_Anon\00039251\3__Ax_T2\1418667184.dcm" 
    output_file = "dicom_fields.txt"
    dicom_to_txt(dicom_file, output_file)
    print(f"Saved DICOM fields to {output_file}")
