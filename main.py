from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from models import TaxData, Token, UserSignup
import uvicorn
from databaseManager import SqliteManager
from utils import check_afm
import sqlite3
import os
from dotenv import load_dotenv
from openai import OpenAI
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from starlette.status import HTTP_401_UNAUTHORIZED
from typing import Dict

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

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        afm: str = payload.get("sub")
        if afm is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = sqlite_manager.get_user_by_afm(afm)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = sqlite_manager.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect AFM or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["afm"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/signup")
def signup(user_signup: UserSignup):
    if sqlite_manager.get_user_by_afm(user_signup.afm):
        raise HTTPException(status_code=400, detail="User with this AFM already exists")
    hashed_password = get_password_hash(user_signup.password)
    sqlite_manager.add_user(user_signup.afm, user_signup.email, hashed_password)
    return {"message": "User created successfully"}

@app.get("/", response_class=FileResponse)
async def get_homepage(current_user: Dict = Depends(get_current_user)):
    return FileResponse("templates/home_page.html")

@app.get("/tables", response_class=FileResponse)
async def get_tables_page(current_user: Dict = Depends(get_current_user)):
    return FileResponse("templates/tables_page.html")

@app.post("/submit")
def submit_tax_data(tax_data: TaxData, current_user: Dict = Depends(get_current_user)):
    try:
        uid = sqlite_manager.save_tax_data(tax_data)
        return {"message": f"The name of the user is {tax_data.name}, submitted by user {current_user['afm']}", "uid": uid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get_tax_submissions")
def get_tax_data(afm: str, current_user: Dict = Depends(get_current_user)):
    if current_user['afm'] != afm:
        raise HTTPException(status_code=403, detail="Not authorized to access this AFM")

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
async def generate_advice(request: Request, current_user: Dict = Depends(get_current_user)):
    print("inside the generateadvice")
    data = await request.json()
    print(f"{data=}")
    tax_details = data
    print(tax_details)
    prompt = f"Provide financial advice based on the following tax details, submitted by user {current_user['afm']}. Show me the values I provide, make comparisons between expenses and revenue, propose ways to increase revenue from the lower income streams, recommend ways to avoid some of the expenses, and make an overall conclusion:\n{tax_details}"
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
    
@app.get("/signup-page", response_class=FileResponse)
async def get_signup_page():
    return FileResponse("templates/signuppage.html")
    
@app.get("/login-page", response_class=FileResponse)
async def get_login_page():
    return FileResponse("templates/log_in_page.html")

@app.exception_handler(HTTP_401_UNAUTHORIZED)
async def custom_401_handler(request: Request, exc: HTTPException):
    # Check if the user has a valid token before redirecting
    token = request.headers.get("Authorization")
    if token:
        token = token.split("Bearer ")[1]
        if not is_token_expired(token):
            return RedirectResponse(url="/tables")
    return RedirectResponse(url="/login-page")

def is_token_expired(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expiry = payload.get("exp")
        if expiry and datetime.now(timezone.utc) < datetime.fromtimestamp(expiry, timezone.utc):
            return False
    except JWTError:
        pass
    return True

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
