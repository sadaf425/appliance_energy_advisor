from fastapi import APIRouter, Depends, HTTPException

from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User, Appliance

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

from functions import (
    calculate_daily_consumption,
    get_monthly_consumption,
    get_cost,
    give_advice
)


router = APIRouter()


# ==================================================
# DATABASE
# ==================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==================================================
# REQUEST MODELS
# ==================================================

class SignupData(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginData(BaseModel):
    email: EmailStr
    password: str


class ApplianceData(BaseModel):
    appliance: str
    power: int
    hours: int


# ==================================================
# SIGNUP
# ==================================================

@router.post("/signup")
def signup(
    data: SignupData,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(data.password)

    new_user = User(
        name=data.name,
        email=data.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "name": new_user.name,
        "email": new_user.email
    }


# ==================================================
# LOGIN
# ==================================================

@router.post("/login")
def login(
    data: LoginData,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ==================================================
# POST APPLIANCE
# ==================================================

@router.post("/appliances")
def post_appliance(
    data: ApplianceData,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    daily = calculate_daily_consumption(
        data.power,
        data.hours
    )

    new_appliance = Appliance(
        user_id=current_user.id,
        appliance=data.appliance,
        power=data.power,
        hours=data.hours,
        daily_units=daily
    )

    db.add(new_appliance)
    db.commit()
    db.refresh(new_appliance)

    return new_appliance


# ==================================================
# GET ALL
# ==================================================

@router.get("/appliances")
def get_appliances(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    appliances = db.query(Appliance).filter(
        Appliance.user_id == current_user.id
    ).all()

    return appliances



# ==================================================
# HIGHEST CONSUMING
# ==================================================

@router.get("/appliances/highest")
def get_highest_appliance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appliances = db.query(Appliance).filter(
        Appliance.user_id == current_user.id
    ).all()

    if not appliances:
        raise HTTPException(
            status_code=404,
            detail="No appliances found"
        )

    high_appliance = None
    high = 0

    for appliance in appliances:
        if appliance.daily_units > high:
            high = appliance.daily_units
            high_appliance = appliance.appliance

    threshold = 8

    if high > threshold:
        advice = "is consuming unusually high energy."
    else:
        advice = "consumption is within a reasonable range."

    return {
        "highest_appliance": high_appliance,
        "daily_consumption": high,
        "advice": f"{high_appliance} {advice}"
    }

# ==================================================
# GET ONE
# ==================================================

@router.get("/appliances/{id}")
def get_appliance(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    appliance = db.query(Appliance).filter(
        Appliance.id == id,
        Appliance.user_id == current_user.id
    ).first()

    if appliance is None:

        raise HTTPException(
            status_code=404,
            detail="Appliance not found"
        )

    return appliance



# ==================================================
# PUT
# ==================================================

@router.put("/appliances/{id}")
def put_appliance(
    id: int,
    data: ApplianceData,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    appliance = db.query(Appliance).filter(
        Appliance.id == id,
        Appliance.user_id == current_user.id
    ).first()

    if appliance is None:

        raise HTTPException(
            status_code=404,
            detail="Appliance not found"
        )

    appliance.appliance = data.appliance
    appliance.power = data.power
    appliance.hours = data.hours

    appliance.daily_units = calculate_daily_consumption(
        data.power,
        data.hours
    )

    db.commit()
    db.refresh(appliance)

    return appliance


# ==================================================
# DELETE
# ==================================================

@router.delete("/appliances/{id}")
def delete_appliance(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    appliance = db.query(Appliance).filter(
        Appliance.id == id,
        Appliance.user_id == current_user.id
    ).first()

    if appliance is None:

        raise HTTPException(
            status_code=404,
            detail="Appliance not found"
        )

    db.delete(appliance)
    db.commit()

    return {
        "message": "Appliance deleted successfully"
    }


# ==================================================
# DAILY SUMMARY
# ==================================================

@router.get("/appliances/summary/daily")
def get_daily_consumption(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    appliances = db.query(Appliance).filter(
        Appliance.user_id == current_user.id
    ).all()

    total = 0

    for appliance in appliances:
        total += appliance.daily_units

    return {
        "daily_units": total
    }


# ==================================================
# MONTHLY SUMMARY
# ==================================================

@router.get("/appliances/summary/monthly")
def get_monthly_consumption_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    appliances = db.query(Appliance).filter(
        Appliance.user_id == current_user.id
    ).all()

    daily = 0

    for appliance in appliances:
        daily += appliance.daily_units

    monthly = get_monthly_consumption(daily)

    cost = get_cost(monthly)

    advice = give_advice(monthly)

    return {
        "monthly_units": monthly,
        "monthly_cost": cost,
        "advice": advice
    }