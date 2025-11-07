#!/usr/bin/env python3

import os
import re
import csv

WORK_DIR = r"Z:\MRI_Report"
IN_FILE = "radMRI.txt"
OUT_FILE = "radMRI_parsed_minimal.csv"

os.chdir(WORK_DIR)

#regex
size_re = re.compile(r'(\d+(?:\.\d+)?\s*cm)', re.IGNORECASE)
pirads_re = re.compile(r'PI[-\s]?RADS[:\s]*([0-5])', re.IGNORECASE)
side_re = re.compile(r'\b(right|left)\b', re.IGNORECASE)
level_re = re.compile(r'\b(base|mid|apex|basilar|apical)\b', re.IGNORECASE)
pz_tz_re = re.compile(r'\b(PZ|TZ|peripheral zone|transition zone)[^\.,;\n]*', re.IGNORECASE)
epe_yes_keywords = ['extraprostatic', 'extracapsular', 'definite extraprostatic', 'likely extension', 'extending beyond prostate', 'possible extraprostatic']
epe_no_keywords = ['no extraprostatic', 'no evidence of extraprostatic', 'no definite extraprostatic', 'without extraprostatic', 'no epe', 'no extraprostatic extension', 'no definite']

prosvol_re = re.compile(r'Prostate (?:Gland )?Size:.*?(\d+(?:\.\d+)?)\s*mL', re.IGNORECASE)
prosvol_re2 = re.compile(r'Prostate Volume:.*?(\d+(?:\.\d+)?)\s*mL', re.IGNORECASE)
prosvol_fallback = re.compile(r'(\d+(?:\.\d+)?)\s*mL', re.IGNORECASE)


def norm(s):
    if not s:
        return "NA"
    s = s.strip()
    return s if s else "NA"

def parse_lesions(report_text, max_lesions=5):

    lesions = []

  
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', report_text) if p.strip()]

   
    candidates = []
    for p in paragraphs:
        low = p.lower()
        if 'focal lesion' in low or 'pi-rads' in low or 'pi rads' in low or ('lesion' in low and 'cm' in low):
            candidates.append(p)

    if not candidates:
        for p in paragraphs:
            if 'cm' in p.lower() and ('pi' in p.lower() or 'lesion' in p.lower()):
                candidates.append(p)

  
    if not candidates:
        for m in pirads_re.finditer(report_text):
            span = report_text[max(0, m.start()-80): m.end()+80]
            candidates.append(span)


    for cand in candidates:
        if len(lesions) >= max_lesions:
            break
        text = cand

        m = size_re.search(text)
        size = m.group(1).strip() if m else "NA"

    
        m = pirads_re.search(text)
        pirads = m.group(1) if m else "NA"

        m = side_re.search(text)
        side = m.group(1).capitalize() if m else "NA"

        m = level_re.search(text)
        level = m.group(1).capitalize() if m else "NA"
   
        if level.lower().startswith('bas'):
            level = 'Base'
        if level.lower().startswith('apic'):
            level = 'Apex'


        m = pz_tz_re.search(text)
        zone = "NA"
        if m:
            z = m.group(0)
    
            if 'pz' in z.lower() or 'peripheral' in z.lower():
                zone = 'PZ'
            elif 'tz' in z.lower() or 'transition' in z.lower():
                zone = 'TZ'
            else:
                zone = z.strip()


        low = text.lower()
        epe = "NA"
        if any(k in low for k in epe_no_keywords):
            epe = "No"
        elif any(k in low for k in epe_yes_keywords):
            epe = "Yes"
        else:

            if 'extraprostatic' in low or 'extracapsular' in low or 'extension' in low:
                epe = "Yes"
            elif 'no evidence' in low and 'extraprostatic' in low:
                epe = "No"

        sv = "NA"
        if 'seminal' in low:
    
            sv = "Yes"

        lesions.append({
            "Size": norm(size),
            "PIRADS": norm(pirads),
            "Side": norm(side),
            "Level": norm(level),
            "Zone": norm(zone),
            "EPE": norm(epe),
            "SV": norm(sv)
        })

    while len(lesions) < max_lesions:
        lesions.append({"Size":"NA","PIRADS":"NA","Side":"NA","Level":"NA","Zone":"NA","EPE":"NA","SV":"NA"})

    return lesions[:max_lesions]

with open(IN_FILE, "r", encoding="utf-8", errors="replace") as f:
    data = f.read()

data = data.replace('\r\n', '\n').replace('\r', '\n')


raw_reports = [r.strip() for r in data.split('report_end') if r.strip()]

header = ["ReportIndex", "PMRN", "Type", "ProsVol"]

for i in range(1, 6):
    header += [f"DIL{i}_Size", f"DIL{i}_PIRADS", f"DIL{i}_Side", f"DIL{i}_Level", f"DIL{i}_Zone", f"DIL{i}_EPE", f"DIL{i}_SV"]

with open(OUT_FILE, "w", newline="", encoding="utf-8") as outcsv:
    writer = csv.writer(outcsv)
    writer.writerow(header)

    report_idx = 0
    for rep in raw_reports:
        report_idx += 1
        lines = rep.split('\n')

        header_line = None
        for ln in lines:
            if ln.strip().upper().startswith("EMPI|"):
                header_line = ln.strip()
                break

        pmrn = "NA"
        rpttype = "NA"
        prosvol = "NA"

        if header_line:
            parts = header_line.split('|')
   
            if len(parts) >= 7:
            
                pmrn = parts[3].strip() if parts[3].strip() else "NA"
         
                rpttype = parts[6].strip() if len(parts) > 6 and parts[6].strip() else "NA"
            else:
            
                if len(parts) > 3:
                    pmrn = parts[3].strip()
                if len(parts) > 6:
                    rpttype = parts[6].strip()

        
        m = prosvol_re.search(rep)
        if not m:
            m = prosvol_re2.search(rep)
        if m:
            prosvol = m.group(1).strip()
        else:
            
            m2 = prosvol_fallback.search(rep)
            if m2:
              
                chunk = rep.lower()
                if 'prostate' in chunk[:chunk.find(m2.group(0))+50] if chunk.find(m2.group(0))!=-1 else True:
                    prosvol = m2.group(1)

        prosvol = norm(prosvol)


        lesions = parse_lesions(rep, max_lesions=5)

   
        row = [report_idx, pmrn, rpttype, prosvol]
        for les in lesions:
            row += [les["Size"], les["PIRADS"], les["Side"], les["Level"], les["Zone"], les["EPE"], les["SV"]]

        writer.writerow(row)

print(f"Parsing complete. Processed {report_idx} reports -> output: {OUT_FILE}")
