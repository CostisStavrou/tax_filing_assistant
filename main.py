import os
import logging
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from models import TaxData, Token, UserSignup
import uvicorn
from postgres_manager import PostgresManager
from utils import check_afm
from dotenv import load_dotenv
from openai import OpenAI
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from starlette.status import HTTP_401_UNAUTHORIZED
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path, override=True)

# Fetch environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize PostgresManager after loading env variables
postgres_manager = PostgresManager()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
client = OpenAI(api_key=OPENAI_API_KEY)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logging.info("Access token created.")
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
            logging.warning("Token validation failed: No AFM found.")
            raise credentials_exception
    except JWTError:
        logging.error("JWTError during token validation.")
        raise credentials_exception
    user = postgres_manager.get_user_by_afm(afm)
    if user is None:
        logging.warning("User not found for provided AFM.")
        raise credentials_exception
    logging.info("User authenticated successfully.")
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if not check_afm(form_data.username):
        logging.warning("Invalid AFM provided during login.")
        raise HTTPException(
            status_code=400,
            detail="Το ΑΦΜ δεν είναι έγκυρο.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = postgres_manager.authenticate_user(form_data.username, form_data.password)
    if not user:
        logging.warning("Incorrect AFM or password.")
        raise HTTPException(
            status_code=400,
            detail="Incorrect AFM or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["afm"], "afm": user["afm"]}, expires_delta=access_token_expires
    )
    logging.info("Access token generated for user.")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/signup", response_model=Token)
def signup(user_signup: UserSignup):
    if not check_afm(user_signup.afm):
        logging.warning("Invalid AFM provided during signup.")
        raise HTTPException(status_code=400, detail="Το ΑΦΜ δεν είναι έγκυρο.")
    
    if postgres_manager.get_user_by_afm(user_signup.afm):
        logging.warning("Attempt to sign up with existing AFM.")
        raise HTTPException(status_code=400, detail="User with this AFM already exists")
    
    hashed_password = get_password_hash(user_signup.password)
    postgres_manager.add_user(user_signup.afm, user_signup.email, hashed_password)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_signup.afm, "afm": user_signup.afm}, expires_delta=access_token_expires
    )
    logging.info("User signed up successfully and access token generated.")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
async def logout():
    logging.info("User logged out successfully.")
    return {"message": "Logged out successfully"}

@app.get("/", response_class=FileResponse)
async def get_homepage(current_user: Dict = Depends(get_current_user)):
    logging.info("Homepage accessed.")
    return FileResponse("templates/home_page.html")

@app.get("/tables", response_class=FileResponse)
async def get_tables_page(current_user: Dict = Depends(get_current_user)):
    logging.info("Tables page accessed.")
    return FileResponse("templates/tables_page.html")

@app.post("/submit")
def submit_tax_data(tax_data: TaxData, current_user: Dict = Depends(get_current_user)):
    try:
        uid = postgres_manager.save_tax_data(tax_data)
        logging.info(f"Tax data submitted for user {current_user['afm']}.")
        return {"message": f"The name of the user is {tax_data.name}, submitted by user {current_user['afm']}", "uid": uid}
    except Exception as e:
        logging.error(f"Error submitting tax data: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get_tax_submissions")
def get_tax_data(current_user: Dict = Depends(get_current_user)):
    afm = current_user['afm']
    logging.debug(f"Fetching tax data for AFM: {afm}.")
    is_valid_afm = check_afm(afm)
    if not is_valid_afm: 
        logging.warning(f"Invalid AFM: {afm}.")
        raise HTTPException(status_code=400, detail=f"The AFM {afm} is not valid")
    try:
        person_info = postgres_manager.get_person_data(afm)
        if not person_info:
            logging.warning(f"No person found with AFM: {afm}.")
            raise HTTPException(status_code=404, detail=f"No person found with AFM {afm}")

        tax_details_info = postgres_manager.get_tax_details(afm)
        logging.info(f"Tax data fetched successfully for AFM: {afm}.")

        return {
            "person_info": person_info,
            "tax_details_info": tax_details_info
        }
    except Exception as e:
        logging.error(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.post("/generate_advice")
async def generate_advice(request: Request, current_user: Dict = Depends(get_current_user)):
    logging.info("Generating financial advice.")
    data = await request.json()
    logging.debug(f"Data received for advice generation: {data}")
    tax_details = data
    prompt = f"Provide financial advice based on the following tax details, submitted by user {current_user['afm']}. Show me the values I provide, make comparisons between expenses and revenue, propose ways to increase revenue from the lower income streams, recommend ways to avoid some of the expenses, and make an overall conclusion:\n{tax_details}"

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        advice = completion.choices[0].message.content
        logging.info("Financial advice generated successfully.")
        return {"message": advice}
    except Exception as e:
        logging.error(f"Error generating advice: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating advice: {e}")
    
@app.get("/signup-page", response_class=FileResponse)
async def get_signup_page():
    logging.info("Signup page accessed.")
    return FileResponse("templates/signuppage.html")
    
@app.get("/login-page", response_class=FileResponse)
async def get_login_page():
    logging.info("Login page accessed.")
    return FileResponse("templates/log_in_page.html")

@app.exception_handler(HTTP_401_UNAUTHORIZED)
async def custom_401_handler(request: Request, exc: HTTPException):
    logging.warning("Unauthorized access attempt detected.")
    token = request.headers.get("Authorization")
    if token:
        token = token.split("Bearer")[1]
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
        logging.error("JWTError during token expiry check.")
    return True

if __name__ == "__main__":
    logging.info("Starting FastAPI application.")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
