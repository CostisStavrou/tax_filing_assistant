from pydantic import BaseModel, Field

class TaxData(BaseModel):
    name: str
    afm: str
    address: str
    family_status: str
    children: int = Field(..., ge=0, title="Children", description="Must be a non-negative integer")
    salary: float = Field(..., ge=0, title="Salary", description="Must be a non-negative number")
    freelance: float = Field(..., ge=0, title="Freelance Income", description="Must be a non-negative number")
    rental: float = Field(..., ge=0, title="Rental Income", description="Must be a non-negative number")
    investments: float = Field(..., ge=0, title="Investment Income", description="Must be a non-negative number")
    business: float = Field(..., ge=0, title="Business Income", description="Must be a non-negative number")
    medical: float = Field(..., ge=0, title="Medical Expenses", description="Must be a non-negative number")
    donations: float = Field(..., ge=0, title="Donations", description="Must be a non-negative number")
    insurance: float = Field(..., ge=0, title="Insurance Payments", description="Must be a non-negative number")
    renovation: float = Field(..., ge=0, title="Renovation Expenses", description="Must be a non-negative number")
    property_details: str
    property_value: float = Field(..., ge=0, title="Property Value", description="Must be a non-negative number")
    vehicles: str
    tax_prepayments: float = Field(..., ge=0, title="Tax Prepayments", description="Must be a non-negative number")
    insurance_payments: float = Field(..., ge=0, title="Insurance Payments", description="Must be a non-negative number")
    
    def validate_afm(cls, afm: str) -> str:
        if len(afm) != 9 or not afm.isdigit():
            raise ValueError('AFM must be exactly 9 digits')
        return afm

    def create(cls, **data):
        afm = data.get('afm')
        data['afm'] = cls.validate_afm(afm)
        return cls(**data)
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class UserSignup(BaseModel):
    afm: str
    email: str
    password: str