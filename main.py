from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from models import TaxData
from fastapi.staticfiles import StaticFiles
import uvicorn
from databaseManager import SqliteManager
from utils import check_afm
import sqlite3
import os
from dotenv import load_dotenv
from openai import OpenAI
from passlib.context import CryptContext

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

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    
@app.get("/tables", response_class=FileResponse)
def get_tables_page():
    return FileResponse("templates/tables_page.html")

@app.get("/get_tax_submissions")
def get_tax_data(afm: str):

    is_valid_afm = check_afm(afm)
    if not is_valid_afm: 
        raise HTTPException(status_code=400, detail=f"The AFM {afm} is not valid")
    try:
        person_info = sqlite_manager.get_person_data(afm)
        if not person_info:
            print(f"No person found with AFM: {afm}")
            raise HTTPException(status_code=404, detail=f"No person found with AFM {afm}")

        tax_details_info = sqlite_manager.get_tax_details(afm)

        print(f"Formatted response data successfully.")

        return {
            "person_info": person_info,
            "tax_details_info": tax_details_info
        }
    except sqlite3.Error:
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.post("/generate_advice")
async def generate_advice(request: Request):
    print("inside the generateadvice")
    data = await request.json()
    print(f"{data=}")
    tax_details = data
    print(tax_details)
    prompt = f"Provide financial advice based on the following tax details, show me the values i provide, make comparisons between expenses and revenue,  propose ways to increase revenue from the lower income streams, recommend way to avoid some of the expenses and make an overall conclusion:\n{tax_details}"
    print(f"{prompt=}")

    try:
        print("before response")
        completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        )

        print(completion.choices[0].message.content)
        advice = completion.choices[0].message.content
        return {"message": advice}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating advice: {e}")
    
#@app.post("/signup")
 
@app.get("/signup-page", response_class=FileResponse)
async def get_signup_page():
    return FileResponse("templates/signuppage.html")

#@app.post("/login")
    
@app.get("/login-page", response_class=FileResponse)
async def get_login_page():
    return FileResponse("templates/log_in_page.html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
