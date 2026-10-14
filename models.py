from pydantic import BaseModel, EmailStr, Field, field_validator

from utils import check_afm


def _validate_afm(afm: str) -> str:
    afm = afm.strip()
    if not check_afm(afm):
        raise ValueError("Το ΑΦΜ δεν είναι έγκυρο (must be 9 digits with a valid check digit).")
    return afm


class TaxData(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    afm: str
    address: str = Field(..., min_length=1, max_length=300)
    family_status: str = Field(..., min_length=1, max_length=100)
    children: int = Field(..., ge=0, le=30, title="Children")
    salary: float = Field(..., ge=0, title="Salary")
    freelance: float = Field(..., ge=0, title="Freelance Income")
    rental: float = Field(..., ge=0, title="Rental Income")
    investments: float = Field(..., ge=0, title="Investment Income")
    business: float = Field(..., ge=0, title="Business Income")
    medical: float = Field(..., ge=0, title="Medical Expenses")
    donations: float = Field(..., ge=0, title="Donations")
    insurance: float = Field(..., ge=0, title="Insurance Payments")
    renovation: float = Field(..., ge=0, title="Renovation Expenses")
    property_details: str = Field(..., max_length=500)
    property_value: float = Field(..., ge=0, title="Property Value")
    vehicles: str = Field(..., max_length=500)
    tax_prepayments: float = Field(..., ge=0, title="Tax Prepayments")
    insurance_payments: float = Field(..., ge=0, title="Insurance Payments")

    _check_afm = field_validator("afm")(_validate_afm)


class Token(BaseModel):
    access_token: str
    token_type: str


class UserSignup(BaseModel):
    afm: str
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)  # bcrypt only uses the first 72 bytes

    _check_afm = field_validator("afm")(_validate_afm)


class AdviceRequest(BaseModel):
    uid: str
