from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import TaxData
import uvicorn

app = FastAPI()

# Add CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/submit")
def submit_tax_data(tax_data: TaxData):
    try:
        print(tax_data)
        return tax_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/homepage")

@app.get("/test")
def test():
    return {"message": "tax catalogue"}

@app.get("/")
def default():
    return {"message": "welcome to my api"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
