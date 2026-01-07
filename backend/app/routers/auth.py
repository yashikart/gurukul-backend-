
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.core.database import get_db
from app.core.config import settings
from app.models.all_models import User, Tenant
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from typing import Optional

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# For Supabase, we might verify using the JWT secret.
# Or if we just trust the frontend sent a valid token validated by Supabase client...
# Ideally we verify signature.
# For this "Yellow Mandate", let's implement a robust check if we had the key.
# If SUPABASE_KEY is missing, we might use a mock logic for dev (Warning: NOT PRODUCTION SAFE but enables progress)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Verify JWT token and return current user from SQLite database"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode and verify JWT token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        email: str = payload.get("sub")  # 'sub' is standard JWT claim for subject (user identifier)
        if email is None:
            raise credentials_exception

        # Get user from database
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
            
        return user
        
    except JWTError:
        raise credentials_exception
    except Exception as e:
        print(f"[Auth] Error: {e}")
        raise credentials_exception

def require_role(role: str):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != role and user.role != "ADMIN": # Admin can do anything
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required Role: {role}"
            )
        return user
    return role_checker

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Find or create default tenant
    default_tenant = db.query(Tenant).filter(Tenant.name == "Gurukul Main").first()
    if not default_tenant:
        default_tenant = Tenant(name="Gurukul Main", type="INSTITUTION")
        db.add(default_tenant)
        db.commit()
        db.refresh(default_tenant)
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name or user_data.email.split("@")[0],
        role=user_data.role.upper(),
        tenant_id=default_tenant.id,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": new_user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role
        }
    }

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    # Find user
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not user.hashed_password or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user
