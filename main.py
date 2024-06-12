from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from models import TaxData
from fastapi.staticfiles import StaticFiles
import uvicorn
from databaseManager import SqliteManager
from utils import check_afm
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.mount("/static", StaticFiles(directory="static"), name="static")

sqlite_manager = SqliteManager() 

@app.get("/", response_class=FileResponse)
async def get_homepage():
    return FileResponse("templates/home_page.html")

@app.post("/submit")
def submit_tax_data(tax_data: TaxData):
    try:
        uid = sqlite_manager.save_tax_data(tax_data)
        return {"message": f"the name of the user is {tax_data.name}", "uid": uid}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get_tax_submissions")
def get_tax_data(afm : str):
    is_valid_afm = check_afm(afm)
    if not is_valid_afm: 
        raise HTTPException(status_code=400, detail=f"the afm {afm} is not valid")
    try:
        conn = sqlite3.connect('tax_database.db')
        cursor = conn.cursor()

        print(f"Connected to database, executing query for person table.")

        # Retrieve data from the person table
        cursor.execute('''
        SELECT * FROM person WHERE afm = ?
        ''', (afm,))
        person_data = cursor.fetchone()

        if not person_data:
            print(f"No person found with AFM: {afm}")
            raise HTTPException(status_code=404, detail=f"No person found with afm {afm}")

        print(f"Person data: {person_data}")

        print(f"Executing query for tax_details table.")

        # Retrieve data from the tax_details table
        cursor.execute('''
        SELECT * FROM tax_details WHERE afm = ?
        ''', (afm,))
        tax_details_data = cursor.fetchall()

        print(f"Tax details data: {tax_details_data}")

        conn.close()

        # Format the response
        person_keys = ["afm", "name", "address", "family_status", "children"]
        tax_details_keys = ["uid", "afm", "salary", "freelance", "rental", "investments", "business", "medical", "donations", "insurance", "renovation", "property_details", "property_value", "vehicles", "tax_prepayments", "insurance_payments", "submission_date"]

        person_info = dict(zip(person_keys, person_data))
        tax_details_info = [dict(zip(tax_details_keys, detail)) for detail in tax_details_data]

        print(f"Formatted response data successfully.")

        return {
            "person_info": person_info,
            "tax_details_info": tax_details_info
        }
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        print(f"Unexpected error: {e}")

@app.get("/test")
def test():
    return {"message": "tax catalogue"} 

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
