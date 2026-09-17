from fastapi import FastAPI, UploadFile, File, Form
from typing import List
import shutil
import os
from backend.engine import parse_schedule_pdf, extract_dancer_roles, filter_dancer_schedule


app = FastAPI(title="Ballet Schedule Parsing Engine")

@app.post("/filter-schedule/")
async def process_schedule(
    dancer_name: str = Form(...),
    opt_out_dates: str = Form(""),  # Comma-separated, e.g., "18.09,25.09"
    schedule_pdf: UploadFile = File(...),
    cast_pdfs: List[UploadFile] = File(...)
):
    os.makedirs("temp", exist_ok=True)
    
    # Save uploaded schedule PDF temporarily
    sched_path = f"temp/{schedule_pdf.filename}"
    with open(sched_path, "wb") as buffer:
        shutil.copyfileobj(schedule_pdf.file, buffer)
        
    # Save uploaded cast list PDFs temporarily
    cast_paths = []
    for cast_file in cast_pdfs:
        c_path = f"temp/{cast_file.filename}"
        with open(c_path, "wb") as buffer:
            shutil.copyfileobj(cast_file.file, buffer)
        cast_paths.append(c_path)
        
    # Parse data using engine logic
    parsed_roles = extract_dancer_roles(cast_paths, dancer_name)
    raw_schedule = parse_schedule_pdf(sched_path)
    
    opt_out_list = [d.strip() for d in opt_out_dates.split(",") if d.strip()]
    
    filtered_sched, feierabend = filter_dancer_schedule(
        raw_schedule, 
        dancer_name, 
        parsed_roles, 
        opt_out_list
    )
    
    # Clean up temporary files
    for path in [sched_path] + cast_paths:
        if os.path.exists(path):
            os.remove(path)
            
    return {
        "dancer": dancer_name,
        "roles_found": parsed_roles,
        "schedule": filtered_sched,
        "feierabend": feierabend
    }
