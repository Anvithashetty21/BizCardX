import re

def parse_extracted(result):
    parsed = {
        "Name": "",
        "Designation": "",
        "Company": "",
        "Contact": "",
        "Email": "",
        "Website": "",
        "Address": "",
        "Pincode": ""
    }

    clean_text = [line.strip() for line in result if len(line.strip()) > 1]

    if len(clean_text) > 0:
        parsed["Name"] = clean_text[0]
    if len(clean_text) > 1:
        parsed["Designation"] = clean_text[1]

    for line in clean_text[2:]:
        if re.search(r'\+?\d[\d\s-]{7,}', line):
            parsed["Contact"] += line + " "
        elif re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.\w+\b', line):
            parsed["Email"] += line + " "
        elif re.search(r'www\.|http|\.com', line, re.IGNORECASE):
            parsed["Website"] += line + " "
        elif re.search(r'\b\d{5,6}\b', line):
            parsed["Pincode"] += line + " "
        elif any(w in line.lower() for w in ["road", "st", "street", "avenue", "lane", "city", "state"]):
            parsed["Address"] += line + " "
        else:
            parsed["Company"] += line + " "

    return {k: v.strip() for k, v in parsed.items()}
