from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from models import TaxData
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from databaseManager import SqliteManager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

templates = Jinja2Templates(directory="backend/templates")

app.mount("/static", StaticFiles(directory="backend/static"), name="static") 

@app.get("/", response_class=HTMLResponse)
async def get_homepage(request: Request):
    return templates.TemplateResponse("home_page.html", {"request": request})

sqlite_manager = SqliteManager()

@app.post("/submit")
def submit_tax_data(tax_data: TaxData):
    try:
        uid = sqlite_manager.save_tax_data(tax_data)
        return {"message": f"the name of the user is {tax_data.name}", "uid": uid}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/test")
def test():
    return {"message": "tax catalogue"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
