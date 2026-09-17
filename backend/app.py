from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from typing import List
import shutil
import os
from backend.engine import parse_schedule_pdf, extract_dancer_roles, filter_dancer_schedule

app = FastAPI(title="Ballet Schedule Parsing Engine")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/filter-schedule/")
async def process_schedule(
    dancer_name: str = Form(...),
    opt_out_dates: str = Form(""),
    schedule_pdf: UploadFile = File(...),
    cast_pdfs: List[UploadFile] = File(...)
):
    os.makedirs("temp", exist_ok=True)
    
    sched_path = f"temp/{schedule_pdf.filename}"
    with open(sched_path, "wb") as buffer:
        shutil.copyfileobj(schedule_pdf.file, buffer)
        
    cast_paths = []
    for cast_file in cast_pdfs:
        c_path = f"temp/{cast_file.filename}"
        with open(c_path, "wb") as buffer:
            shutil.copyfileobj(cast_file.file, buffer)
        cast_paths.append(c_path)
        
    parsed_roles = extract_dancer_roles(cast_paths, dancer_name)
    raw_schedule = parse_schedule_pdf(sched_path)
    
    opt_out_list = [d.strip() for d in opt_out_dates.split(",") if d.strip()]
    
    filtered_sched, feierabend = filter_dancer_schedule(
        raw_schedule, 
        dancer_name, 
        parsed_roles, 
        opt_out_list
    )
    
    for path in [sched_path] + cast_paths:
        if os.path.exists(path):
            os.remove(path)
            
    return {
        "dancer": dancer_name,
        "roles_found": parsed_roles,
        "schedule": filtered_sched,
        "feierabend": feierabend
    }
