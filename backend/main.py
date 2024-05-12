from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
from openpyxl import load_workbook
import sqlite3
import shutil

app = FastAPI()

# Connect to SQLite database
conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS people
                  (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT)''')

@app.get("/download/{file_name}")
async def download_file(file_name: str):
    # Read new data from text file and insert into SQLite database
    with open('files/dane.txt', 'r') as file:
        lines = file.readlines()

    cursor.execute('''DELETE FROM people''')
    shutil.copy("formatka.xlsx",file_name)

    # Split each line into first name, last name, and ID and insert into SQLite
    for line in lines:
        first_name, last_name, id = line.strip().split()
        cursor.execute('''INSERT OR REPLACE INTO people (first_name, last_name, id) VALUES (?, ?, ?)''',
                       (first_name, last_name, id))
    conn.commit()

    # Load existing Excel file
    wb = load_workbook(file_name)
    ws = wb.active

    # Retrieve data from SQLite database
    cursor.execute('''SELECT * FROM people''')
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

    return FileResponse(file_path, filename=file_name)
