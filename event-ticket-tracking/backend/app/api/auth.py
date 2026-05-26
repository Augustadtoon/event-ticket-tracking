from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_db, hash_password, verify_password, create_token
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="A user with this email already exists"
        )
    
    # Create user based on role
    role_norm = user.role.lower()
    if "admin" in role_norm:
        new_user = User(
            name=user.name,
            email=user.email.lower(),
            password=hash_password(user.password),
            role="admin",
            organization=user.organization,
            position=user.position
        )
    else:
        new_user = User(
            name=user.name,
            email=user.email.lower(),
            password=hash_password(user.password),
            role="student",
            student_number=user.student_number,
            year_level=user.year_level,
            department=user.department,
            course=user.course
        )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email.lower()).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid email or password"
        )

    token = create_token({"user_id": db_user.id, "role": db_user.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": db_user.role
    }