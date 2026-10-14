import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
import psycopg2
from jose import JWTError, jwt
from openai import OpenAI
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED

from postgres_manager import PostgresManager
from models import AdviceRequest, TaxData, Token, UserSignup
from utils import check_afm

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("tax_assistant")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set. Copy .env.example to .env and fill it in.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

app = FastAPI(title="Tax Filing Assistant")
app.mount("/static", StaticFiles(directory="static"), name="static")

db = PostgresManager()
db.create_tables()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Financial advice is unavailable: OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


# ---------- authentication ----------

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        afm = payload.get("sub")
        if afm is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.get_user_by_afm(afm)
    if user is None:
        raise credentials_exception
    return user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if not check_afm(form_data.username):
        raise HTTPException(status_code=400, detail="Το ΑΦΜ δεν είναι έγκυρο.")

    user = db.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect AFM or password")

    logger.info("User logged in")
    access_token = create_access_token(data={"sub": user["afm"], "afm": user["afm"]})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/signup", response_model=Token)
def signup(user_signup: UserSignup):
    if db.get_user_by_afm(user_signup.afm):
        raise HTTPException(status_code=400, detail="User with this AFM already exists")
    try:
        db.add_user(user_signup.afm, user_signup.email, get_password_hash(user_signup.password))
    except psycopg2.IntegrityError:
        raise HTTPException(status_code=400, detail="User with this AFM already exists")

    logger.info("New user signed up")
    access_token = create_access_token(data={"sub": user_signup.afm, "afm": user_signup.afm})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/logout")
async def logout():
    # Tokens are stateless JWTs: the client logs out by deleting its token, which expires after 10 minutes anyway.
    return {"message": "Logged out successfully"}


# ---------- tax data ----------

@app.post("/submit")
def submit_tax_data(tax_data: TaxData, current_user: Dict = Depends(get_current_user)):
    if tax_data.afm != current_user["afm"]:
        logger.warning("Rejected a submission for a different AFM than the logged-in user")
        raise HTTPException(status_code=403, detail="You can only submit a tax return for your own AFM.")
    try:
        uid = db.save_tax_data(tax_data)
    except psycopg2.Error:
        logger.exception("Failed to save tax submission")
        raise HTTPException(status_code=500, detail="Could not save the submission.")
    return {"message": "Submission saved.", "uid": uid}


@app.get("/get_tax_submissions")
def get_tax_data(current_user: Dict = Depends(get_current_user)):
    afm = current_user["afm"]
    try:
        return {
            "person_info": db.get_person_data(afm),
            "tax_details_info": db.get_tax_details(afm),
        }
    except psycopg2.Error:
        logger.exception("Failed to load tax submissions")
        raise HTTPException(status_code=500, detail="Internal server error")


ADVICE_FIELDS = {
    "salary": "Salary income",
    "freelance": "Freelance income",
    "rental": "Rental income",
    "investments": "Investment income",
    "business": "Business income",
    "medical": "Medical expenses",
    "donations": "Donations",
    "insurance": "Insurance",
    "renovation": "Renovation expenses",
    "property_value": "Property value",
    "property_details": "Property details",
    "vehicles": "Vehicles",
    "tax_prepayments": "Tax prepayments",
    "insurance_payments": "Insurance payments",
}


def build_advice_prompt(submission: Dict) -> str:
    # Only the figures are sent to the model: no name, AFM or address.
    lines = [f"- {label}: {submission[key]}" for key, label in ADVICE_FIELDS.items()]
    return (
        "Provide financial advice based on the following tax details (amounts in euros). "
        "Show me the values I provide, make comparisons between expenses and revenue, propose ways to "
        "increase revenue from the lower income streams, recommend ways to avoid some of the expenses, "
        "and make an overall conclusion:\n" + "\n".join(lines)
    )


@app.post("/generate_advice")
def generate_advice(request: AdviceRequest, current_user: Dict = Depends(get_current_user)):
    submission = db.get_submission(request.uid, current_user["afm"])
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    client = get_openai_client()
    try:
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Make clear that this is general "
                                              "information, not professional tax or financial advice."},
                {"role": "user", "content": build_advice_prompt(submission)},
            ],
        )
    except Exception:
        logger.exception("OpenAI request failed")
        raise HTTPException(status_code=502, detail="Error generating advice. Please try again later.")
    return {"message": completion.choices[0].message.content}


# ---------- pages ----------
# The HTML pages contain no user data, so they are served without authentication.
# Each page's JavaScript checks for a valid token and loads data from the protected API endpoints above.

@app.get("/", response_class=FileResponse)
async def get_homepage():
    return FileResponse("templates/home_page.html")


@app.get("/tables", response_class=FileResponse)
async def get_tables_page():
    return FileResponse("templates/tables_page.html")


@app.get("/signup-page", response_class=FileResponse)
async def get_signup_page():
    return FileResponse("templates/signuppage.html")


@app.get("/login-page", response_class=FileResponse)
async def get_login_page():
    return FileResponse("templates/log_in_page.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
