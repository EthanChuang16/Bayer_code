import os 
import sys
import pydicom
from pydicom.uid import UID
from pydicom.valuerep import PersonName
import hashlib
import shutil
from datetime import datetime


#helper functions
#For UID fields

def transform_uid_sha256(original_uid: str) -> str:
    """
    Deterministically transform a UID using SHA-256 hashing,
    producing a valid anonymized DICOM UID starting with '2.25.'.
   
    Args:
        original_uid (str): Original UID to anonymize.
   
    Returns:
        str: Transformed DICOM UID.
    """
    sha256 = hashlib.sha256(original_uid.encode('utf-8')).digest()
    # Convert to int then to base-10 string
    hashed_int = int.from_bytes(sha256, byteorder='big')
    base10_str = str(hashed_int)

    # Prefix with 2.25 per DICOM spec for numeric-only UIDs
    uid = f"2.25.{base10_str}"

    # Truncate only if full string exceeds 64, and only at valid boundary
    if len(uid) > 64:
        # Remove from the end, not in the middle of a number
        uid = uid[:64]
        if uid[-1] == '.':
            uid = uid[:-1]
    
    return UID(uid)  # Ensures it's a valid UID object

#For fields, 
# (0008,0050): Accession number
# (0010,0010): Patient's Name
# (0010,0020): Patient's ID
# (0010,1000): Other patient ID
# (0020,0010): Study ID
# (0040,0253): Performed procedure step ID
# (0040,1001): Requested procedure ID


def hash_string(input_str: str, length: int = 16) -> str:
    """
    Hashes the input string using SHA-256 and returns a fixed-length
    hexadecimal string.

    Args:
        input_str (str): Original string to hash.
        length (int): Length of the output hash string (max 64).

    Returns:
        str: Hashed string in hex format.
    """
    sha256_hash = hashlib.sha256(input_str.encode('utf-8')).hexdigest()
    return sha256_hash[:length]

#fields to anonymize

tags_to_mask = {
    #(0x0010, 0x0010),  # Patient's Name
    #(0x0010, 0x0020),  # Patient ID
    (0x0010, 0x0030),  # Patient's Birth Date
    (0x0010, 0x0032),  # Patient's Birth Time
    (0x0010, 0x0040),  # Patient's Sex
    #(0x0010, 0x1000),  # Other Patient IDs
    (0x0010, 0x1001),  # Other Patient Names
    (0x0010, 0x1040),  # Patient's Address
    (0x0010, 0x2154),  # Patient's Telephone Numbers
    (0x0010, 0x4000),  # Patient Comments
    (0x0008, 0x0090),  # Referring Physician's Name
    (0x0008, 0x1048),  # Physician(s) of Record
    (0x0008, 0x1060),  # Name of Physician(s) Reading Study
    (0x0008, 0x1010),  # Station Name
    (0x0008, 0x1040),  # Institutional Department Name
    (0x0008, 0x1070),  # Operators’ Name
    (0x0018, 0x1000),  # Device Serial Number
    (0x0008, 0x0020),  # Study Date
    (0x0008, 0x0030),  # Study Time
    (0x0008, 0x0021),  # Series Date
    (0x0008, 0x0031),  # Series Time
    (0x0008, 0x0022),  # Acquisition Date
    (0x0008, 0x0032),  # Acquisition Time
    (0x0008, 0x0023),  # Content Date
    (0x0008, 0x0033),  # Content Time
    (0x0040, 0xA124),  # UID
    #(0x0008, 0x0050),  # Accession Number
    (0x0008, 0x0080),  # Institution Name
    (0x0010, 0x1010),  # Patient's Age   
    (0x0010, 0x1020),  # Patient's Size      
    (0x0010, 0x1030),  # Patient's Weight  
    (0x0008, 0x0012),  # Instance Creation Date
    (0x0008, 0x0013),  # Instance Creation Time
    (0x0008, 0x0016),  # SOP Class UID
    (0x0008, 0x0018),  # SOP Instance UID
    (0x0008, 0x0081),  # Institution Address
    (0x0008, 0x1030),  # Study Description
    (0x0010, 0x2150),  # Country of Residence
    (0x0010, 0x2160),  # Ethnic Group
    (0x0010, 0x21A0),  # Smoking Status
    (0x0010, 0x21C0),  # Pregnancy Status
    (0x0010, 0x21F0),  # Patient's Religious Preference
    (0x0012, 0x0020),  # Clinical Trial Protocol ID
    (0x0012, 0x0031),  # Clinical Trial Site Name
    (0x0012, 0x0042),  # Clinical Trial Subject Reading ID
    (0x0018, 0x0015),  # Body Part Examined
    (0x0032, 0x1032),  # Requesting Physician
    (0x0002, 0x0003),  # Media Storage SOP Instance UID
    (0x0002, 0x0012),  # Implementation Class UID
    (0x0008, 0x1111),  # Referenced Performed Procedure Step Sequence
    (0x0008, 0x1140),  # Referenced Image Sequence
    (0x0008, 0x1155),  # Referenced SOP Instance UID
    (0x0009, 0x0010),  # Private Creator
    (0x0009, 0x2001),  # Private Tag
    (0x0009, 0x1027),  # Private Tag
    (0x0009, 0x1030),  # Private Tag
    (0x0009, 0x10E3),  # Private Tag
    (0x0009, 0x10E9),  # Private Tag
    (0x0010, 0x1021),  # Patient's Size (alternate)
    (0x0010, 0x21B0),  # Additional Patient History
    (0x0020, 0x000D),  # Study Instance UID
    (0x0020, 0x000E),  # Series Instance UID
    #(0x0020, 0x0010),  # Study ID
    (0x0040, 0x0242),  # Performed Station AE Title
    (0x0040, 0x0243),  # Performed Station Name
    #(0x0040, 0x0253),  # Performed Procedure Step ID
    #(0x0040, 0x1001),  # Requested Procedure ID
    #ge tags
    (0x0025, 0x101B),  # [Protocol Data Block (compressed)]
    (0x0043, 0x1028),  # [Unique image identifier]
    (0x0043, 0x102A),  # [User defined data]
    (0x0043, 0x1029),  # [Histogram tables]
    (0x0020, 0x0052),  # Frame of Reference UID
    (0x0040, 0x0244),  # Performed Procedure Step Start Date
    (0x0040, 0x0245),  # Performed Procedure Step Start Time
    (0x0040, 0x0009),  # Scheduled Procedure Step ID
    (0x0400, 0x0561),  # Original Attributes Sequence
    (0x0400, 0x0562),  # Attribute Modification DateTime
    (0x0400, 0x0563),  # Modifying System
    (0x0400, 0x0564),  # Source of Previous Values
    (0x0400, 0x0565),  # Reason for the Attribute Modification
    (0x2110, 0x0030),  # Printer Name
    (0x0008, 0x002A),  # Acquisition DateTime
    (0x0040, 0x0275),  # Request Attributes Sequence
    (0x0040, 0x2016),  # Placer Order Number / Imaging Service Request
    (0x0040, 0x2017),  # Filler Order Number / Imaging Service Request

    (0x0008, 0x103E),  # Series Description
    (0x0008, 0x1110),  # Referenced Study Sequence
    (0x0012, 0x0082),  # Clinical Trial Protocol Ethics Committee Approval Number
    (0x0010, 0x0021),  # Issuer of Patient ID

    (0x0040, 0xA170),  # Purpose of Reference Code Sequence
    (0x0008, 0x0100),  # Code Value
    (0x0008, 0x0102),  # Coding Scheme Designator
    (0x0008, 0x0104),  # Code Meaning
    (0x0012, 0x0062),  # Patient Identity Removed

    (0x0019, 0x109D),  # Pulse Sequence Date
    (0x0043, 0x1061),  # Scanner Study Entity UID
    (0x0008, 0x1250),  # Related Series Sequence
    (0x0008, 0x1150),  # Referenced SOP Class UID (if not already added)
    (0x0008, 0x1160),  # Referenced Frame Number
    (0x0029, 0x1009),  # Siemens CSA Header Info (may contain PHI)
    (0x0029, 0x1019),  # Siemens CSA Header Info (may contain PHI)


}

#fields to hash

hash_string_tags = {
    (0x0008, 0x0050),  # Accession number
    (0x0010, 0x0010),  # Patient's Name
    #(0x0010, 0x0020),  # Patient's ID special case now
    (0x0010, 0x1000),  # Other patient ID
    (0x0020, 0x0010),  # Study ID
    (0x0040, 0x0253),  # Performed procedure step ID
    (0x0040, 0x1001),  # Requested procedure ID
    (0x0038, 0x0010),  #Admission ID
}

#anonymize function

def anonymize_element(ds, elem, tag_tuple, new_patient_id):
   if elem.VR == "SQ":
      #recursively anon items in seq
      for item in elem.value:
         for sub_elem in item.iterall():
            tag_nested = (sub_elem.tag.group, sub_elem.tag.element)
            anonymize_element(item, sub_elem, tag_nested, new_patient_id)
   elif tag_tuple in hash_string_tags:
        if tag_tuple == (0x0010, 0x0010):  # Patient Name
            elem.value = PersonName(hash_string(str(elem.value)))
        else:
            elem.value = hash_string(str(elem.value))
   elif tag_tuple == (0x0010, 0x0020):  # Patient ID
       elem.value = new_patient_id
   elif tag_tuple in tags_to_mask:
       if "UID" in elem.name.upper():
           elem.value = transform_uid_sha256(str(elem.value))
       else:
           elem.value = ""
           #additional log for private ones 
           if tag_tuple in {(0x0029, 0x1009), (0x0029, 0x1019)}:
               print(f"Removed Siemens Private tag: {elem.name} ({tag_tuple})")



#main script 


if __name__ == "__main__":
   if len(sys.argv) != 2:
        print("Usage: python DICOM_Anon.py <original_series_path>")
        sys.exit(1)
   original_series_path = sys.argv[1]
   if not os.path.exists(original_series_path):
        print(f"Provided path does not exist: {original_series_path}")
        sys.exit(1)


   # Get new patient ID from path
   path_parts = os.path.normpath(original_series_path).split(os.sep)
   try:
        dfci_index = path_parts.index("DFCI")
        new_patient_id = path_parts[dfci_index + 1]
   except ValueError:
        print("Could not determine patient ID from path. Must contain 'DFCI'")
        sys.exit(1) 

   #copy to new anonymized folder 
   copy_series_path = original_series_path + "_copy"
   if os.path.exists(copy_series_path):
        print(f"Removing old copy: {copy_series_path}")
        shutil.rmtree(copy_series_path)
   print(f"Copying series to: {copy_series_path}")
   shutil.copytree(original_series_path, copy_series_path)

   print("Running anonymization...")


   printed = False

   for filename in os.listdir(copy_series_path):
        filepath = os.path.join(copy_series_path, filename)
        if not filename.lower().endswith(".dcm"):
            continue
        try:
            ds = pydicom.dcmread(filepath)
            for elem in ds.iterall():
                tag_tuple = (elem.tag.group, elem.tag.element)
                anonymize_element(ds, elem, tag_tuple, new_patient_id)

            # print(f"\n--- {filename} ---")
            # for elem in ds.iterall():
            #     if elem.VR not in ("OB", "OW", "UN", "OF", "UT") and elem.tag != (0x7fe0, 0x0010):
            #         print(f"{elem.name} ({elem.tag}) → {elem.value}")
            if not printed:
                # print(f"\n--- {filename} (Anonymized Fields Preview) ---")
                # for elem in ds.iterall():
                #     if elem.VR not in ("OB", "OW", "UN", "OF", "UT") and elem.tag != (0x7fe0, 0x0010):
                #         print(f"{elem.name} ({elem.tag}) → {elem.value}")
                # printed = True  # Don't print for other files
                print(f"\n--- {filename} (Anonymized Fields Preview written to CSV) ---")
    
                series_parent_dir = os.path.dirname(original_series_path)
                # csv_filename = os.path.join(series_parent_dir, f"anonymized_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                # with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
                #     writer = csv.writer(csvfile)
                #     writer.writerow(["Tag Name", "Tag Number", "Anonymized Value"])

                #     for elem in ds.iterall():
                #         if elem.VR not in ("OB", "OW", "UN", "OF", "UT") and elem.tag != (0x7fe0, 0x0010):
                #             writer.writerow([elem.name, f"({elem.tag.group:04X}, {elem.tag.element:04X})", str(elem.value)])
                # print(f"Anonymized tag data written to: {csv_filename}")
                txt_filename = os.path.join(series_parent_dir, f"anonymized_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                with open(txt_filename, mode='w', encoding='utf-8') as txtfile:
                    txtfile.write("Anonymized Fields Preview:\n")
                    txtfile.write(f"{'Tag Name':40} {'Tag Number':20} {'Anonymized Value'}\n")
                    txtfile.write("=" * 100 + "\n")

                    for elem in ds.iterall():
                        if elem.VR not in ("OB", "OW", "UN", "OF", "UT") and elem.tag != (0x7fe0, 0x0010):
                            tag_str = f"({elem.tag.group:04X}, {elem.tag.element:04X})"
                            line = f"{elem.name:40} {tag_str:20} {str(elem.value)}\n"
                            txtfile.write(line)

                print(f"Anonymized tag data written to: {txt_filename}")

                printed = True
                ds.save_as(filepath)
        except Exception as e:
            print(f"Error: processing {filename}: {e}")


            print("Anonymization complete")
# #hardcode for testing just try to list on a specific path the tags 
# original_series_path = r"Z:\DFCI\90526484\E16694825\MR\2150_ADC__10__6_"
# copy_series_path = original_series_path + "_copy"


# #if an old copy exists, remove it
# if os.path.exists(copy_series_path):
#    print(f"Removing old copy: {copy_series_path}")
#    shutil.rmtree(copy_series_path)

# #copy the original series directory
# print(f"Copying series to: {copy_series_path}")
# shutil.copytree(original_series_path, copy_series_path)



# print("Running DICOM Script")

# #loop through DICOM files 
# for filename in os.listdir(copy_series_path):
#   filepath = os.path.join(copy_series_path, filename)

#   #skip non-dicom files 
#   if not filename.lower().endswith('.dcm'):
#     continue 

#   try:
#     ds = pydicom.dcmread(filepath)
#     # print(f"\n--- DICOM File: {filename} ---")
#     #apply anon to each element
#     for elem in ds.iterall():
#       tag_tuple = (elem.tag.group, elem.tag.element)
#       anonymize_element(ds, elem, tag_tuple)
#     #save the anon file in place
#     ds.save_as(filepath)

#   except Exception as e:
#     print(f"Error reading {filename} : {e}")



# print(f"\n--- DICOM File: {filename} ---")
# for elem in ds.iterall():
#     tag_tuple = (elem.tag.group, elem.tag.element)
#     try:
#         value = elem.value
#         # Filter out very large binary blobs or pixel data
#         if elem.VR in ("OB", "OW", "UN", "OF", "UT") or elem.tag == (0x7fe0, 0x0010):
#             print(f"{elem.name} ({tag_tuple}) -> <binary data omitted>")
#         else:
#             print(f"{elem.name} ({tag_tuple}) -> {value}")
#     except Exception as e:
#         print(f"{elem.name} ({tag_tuple}) -> <unreadable: {e}>")

# print("Anonymization complete")


