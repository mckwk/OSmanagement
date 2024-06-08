from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openpyxl import load_workbook
import sqlite3
import os
import shutil
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allow CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Connect to SQLite database
conn = sqlite3.connect('my_database.db', check_same_thread=False)
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                  id INTEGER PRIMARY KEY,
                  name TEXT,
                  surname TEXT,
                  faculty TEXT,
                  student_id TEXT,
                  phone TEXT,
                  email TEXT,
                  joining_date TEXT,
                  position TEXT
                  )''')
conn.commit()

@app.post("/add_student")
async def add_student(
    name: str = Form(...),
    surname: str = Form(...),
    faculty: str = Form(...),
    student_id: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    joining_date: str = Form(...),
    position: str = Form(...)
):
    try:
        logger.info(f"Adding student: {name} {surname}")
        cursor.execute('''INSERT INTO students (name, surname, faculty, student_id, phone, email, joining_date, position)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                       (name, surname, faculty, student_id, phone, email, joining_date, position))
        conn.commit()
        logger.info("Student added successfully")
        return {
            "message": "Student added successfully",
            "name": name,
            "surname": surname,
            "faculty": faculty,
            "student_id": student_id,
            "phone": phone,
            "email": email,
            "joining_date": joining_date,
            "position": position
        }
    except Exception as e:
        logger.error(f"Error adding student: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while adding the student: {str(e)}")

@app.get("/download/{file_name}")
async def download_file(file_name: str):
    try:
        logger.info(f"Generating report and downloading file: {file_name}")
        # Read new data from text file and insert into SQLite database
        with open('files/dane.txt', 'r') as file:
            lines = file.readlines()

        cursor.execute('''DELETE FROM students''')
        shutil.copy("formatka.xlsx", file_name)

        # Split each line into first name, last name, and ID and insert into SQLite
        for line in lines:
            first_name, last_name, id = line.strip().split()
            cursor.execute('''INSERT OR REPLACE INTO students (name, surname, student_id) VALUES (?, ?, ?)''',
                           (first_name, last_name, id))
        conn.commit()

        # Load existing Excel file
        wb = load_workbook(file_name)
        ws = wb.active

        # Retrieve data from SQLite database
        cursor.execute('''SELECT * FROM students''')
        rows = cursor.fetchall()

        # Set starting position
        start_row = 4
        start_col = 2

        # Write data from database to existing Excel file
        for row_idx, row_data in enumerate(rows, start=start_row):
            for col_idx, value in enumerate(row_data, start=start_col):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.value = value

        # Save changes to the file
        wb.save(file_name)

        file_path = file_name  # Path to your Excel file, adjust accordingly
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File '{file_name}' not found at path: {file_path}")
        elif not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail=f"Path '{file_path}' is not a file")

        logger.info(f"File {file_name} generated and ready for download")
        return FileResponse(file_path, filename=file_name)
    except Exception as e:
        logger.error(f"Error generating membership report: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while generating the membership report: {str(e)}")

@app.get("/students")
async def get_students():
    try:
        cursor.execute('''SELECT * FROM students''')
        students = cursor.fetchall()
        return JSONResponse(content={"students": students})
    except Exception as e:
        logger.error(f"Error fetching students: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching students")

@app.get("/students/{student_id}")
async def get_student(student_id: str):
    try:
        cursor.execute('''SELECT * FROM students WHERE student_id = ?''', (student_id,))
        student = cursor.fetchone()
        if student is None:
            raise HTTPException(status_code=404, detail="Student not found")
        return JSONResponse(content={"student": student})
    except Exception as e:
        logger.error(f"Error fetching student {student_id}: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching the student: {str(e)}")

# Make sure to close the database connection when the application is shut down
@app.on_event("shutdown")
def shutdown_event():
    conn.close()
    logger.info("Database connection closed")