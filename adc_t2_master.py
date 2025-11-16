import os
import subprocess

ROOT = r"Z:\250_bucket"
CONVERTER = "convert_adc_t2.py"

def is_adc_series(name):
    name = name.lower()
    return "adc" in name

def is_t2_series(name):
    name = name.lower()
    return "t2" in name or "t2w" in name

def run_conversion(series_path):
    print(f"  → Converting: {series_path}")
    try:
        subprocess.run(["python", CONVERTER, series_path], check=True)
    except subprocess.CalledProcessError:
        print(f"  !! ERROR converting {series_path}")

def main():
    print("=== Starting ADC / T2 NIfTI Conversion ===")

    for patient in os.listdir(ROOT):
        patient_path = os.path.join(ROOT, patient)
        if not os.path.isdir(patient_path):
            continue

        print(f"\nProcessing patient: {patient}")

        # Loop through series inside the patient folder
        for series in os.listdir(patient_path):
            series_path = os.path.join(patient_path, series)

            if not os.path.isdir(series_path):
                continue

            # Identify ADC / T2 series
            if is_adc_series(series):
                print(f" Found ADC series: {series}")
                run_conversion(series_path)

            elif is_t2_series(series):
                print(f" Found T2 series: {series}")
                run_conversion(series_path)

            else:
                # Not ADC/T2 → skip
                continue

    print("\n=== DONE: All ADC/T2 conversions completed ===")


if __name__ == "__main__":
    main()
