import pdfplumber
import re

def extract_dancer_roles(cast_pdf_paths, dancer_name):
    """
    Reads cast PDFs and finds all roles assigned to the dancer.
    """
    matched_roles = set()
    dancer_name_clean = dancer_name.lower().strip()
    
    for pdf_path in cast_pdf_paths:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                for line in lines:
                    if dancer_name_clean in line.lower():
                        parts = [p.strip() for p in line.split('|') if p.strip()]
                        for part in parts:
                            if dancer_name_clean not in part.lower():
                                matched_roles.add(part)
                                
    return list(matched_roles)


def parse_schedule_pdf(schedule_pdf_path):
    """
    Reads weekly schedule PDF and extracts raw lines per day block.
    """
    days = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    raw_days_data = {}
    current_day = None

    with pdfplumber.open(schedule_pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            for line in lines:
                line_str = line.strip()
                
                for day_prefix in ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]:
                    if line_str.startswith(day_prefix):
                        date_match = re.search(r'\d{1,2}\.\d{1,2}', line_str)
                        date_str = date_match.group(0) if date_match else ""
                        
                        short_prefix = day_prefix[:2]
                        if day_prefix == "Mittwoch": short_prefix = "Mi"
                        if day_prefix == "Dienstag": short_prefix = "Di"
                        if day_prefix == "Donnerstag": short_prefix = "Do"
                        if day_prefix == "Freitag": short_prefix = "Fr"
                        if day_prefix == "Samstag": short_prefix = "Sa"
                        if day_prefix == "Sonntag": short_prefix = "So"
                        
                        current_day = f"{short_prefix} {date_str}".strip()
                        if current_day not in raw_days_data:
                            raw_days_data[current_day] = []
                        break
                
                if current_day and line_str:
                    raw_days_data[current_day].append(line_str)
                    
    return raw_days_data


def filter_dancer_schedule(schedule_data, dancer_name, dancer_roles, opt_out_casts=[]):
    """
    Filters rehearsals based on dancer rules.
    """
    filtered_schedule = {}
    feierabend_dict = {}

    for day, lines in schedule_data.items():
        filtered_schedule[day] = []
        last_end_time = "00:00"

        for line in lines:
            # Always include mandatory morning training
            if "Training" in line and "freiw." not in line and "freiwillig" not in line:
                filtered_schedule[day].append(line)
                continue

            # Skip opt-out / ohne Bes. matches
            skip_line = False
            for opt_date in opt_out_casts:
                if f"ohne Bes. {opt_date}" in line:
                    skip_line = True
                    break
            if skip_line:
                continue

            # Include Entire Cast
            if "Entire Cast" in line or "Entire" in line:
                filtered_schedule[day].append(line)
                continue

            # Match Dancer Name or Roles
            is_match = False
            if dancer_name.lower() in line.lower():
                is_match = True
            else:
                for role in dancer_roles:
                    if role.lower() in line.lower():
                        is_match = True
                        break

            if is_match:
                filtered_schedule[day].append(line)

            # Calculate Feierabend (End time of mandatory work)
            if is_match or "Entire Cast" in line:
                times = re.findall(r'\b\d{2}:\d{2}\b', line)
                if times:
                    last_time = times[-1]
                    if last_time > last_end_time:
                        last_end_time = last_time

        feierabend_dict[day] = last_end_time

    return filtered_schedule, feierabend_dict
